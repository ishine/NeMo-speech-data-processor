# Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd
from tqdm import tqdm

from sdp.logging import logger
from sdp.processors.base_processor import (
    BaseParallelProcessor,
    BaseProcessor,
    DataEntry,
    LegacyParallelProcessor,
)
from sdp.utils.common import load_manifest


class Subprocess(BaseProcessor):
    """
    Processor for handling subprocess execution with additional features for managing input and output manifests.

    Args:
        cmd (str): The command to be executed as a subprocess.
        input_manifest_arg (str, optional): The argument specifying the input manifest. Defaults to an empty string.
        output_manifest_arg (str, optional): The argument specifying the output manifest. Defaults to an empty string.
        arg_separator (str, optional): The separator used between argument and value. Defaults to "=".
        **kwargs: Additional keyword arguments to be passed to the base class.

    Example:
        
        _target_: sdp.processors.datasets.commoncrawl.Subprocess
        output_manifest_file: /workspace/manifest.json
        input_manifest_arg: "--manifest"
        output_manifest_arg: "--output_filename"
        arg_separator: "="
        cmd: "python /workspace/NeMo-text-processing/nemo_text_processing/text_normalization/normalize_with_audio.py \
            --language=en --n_jobs=-1 --batch_size=600 --manifest_text_field=text --cache_dir=${workspace_dir}/cache --overwrite_cache \
            --whitelist=/workspace/NeMo-text-processing/nemo_text_processing/text_normalization/en/data/whitelist/asr_with_pc.tsv"

    """

    def __init__(
        self,
        cmd: str,
        input_manifest_arg: str = "",
        output_manifest_arg: str = "",
        arg_separator: str = "=",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.input_manifest_arg = input_manifest_arg
        self.output_manifest_arg = output_manifest_arg
        self.arg_separator = arg_separator
        self.cmd = cmd

    def process(self):
        os.makedirs(os.path.dirname(self.output_manifest_file), exist_ok=True)
        if self.cmd.find(self.input_manifest_file) != -1 or self.cmd.find(self.output_manifest_file) != -1:
            logger.error(
                "input_manifest_file "
                + self.input_manifest_file
                + " and output_manifest_file "
                + self.output_manifest_file
                + " should be exluded from cmd line!"
            )
            raise ValueError
        process_args = [x for x in self.cmd.split(" ") if x]
        if self.arg_separator == " ":
            if self.input_manifest_arg:
                process_args.extend([self.input_manifest_arg, self.input_manifest_file])
            if self.output_manifest_arg:
                process_args.extend([self.output_manifest_arg, self.output_manifest_file])
        else:
            if self.input_manifest_arg:
                process_args.extend([self.input_manifest_arg + self.arg_separator + self.input_manifest_file])
            if self.output_manifest_arg:
                process_args.extend([self.output_manifest_arg + self.arg_separator + self.output_manifest_file])
        subprocess.run(" ".join(process_args), shell=True)



class CombineSources(BaseParallelProcessor):
    """Can be used to create a single field from two alternative sources.

    E.g.::

        _target_: sdp.processors.CombineSources
        sources:
            - field: text_pc
              origin_label: original
            - field: text_pc_pred
              origin_label: synthetic
            - field: text
              origin_label: no_pc
        target: text

    will populate the ``text`` field with data from ``text_pc`` field if it's
    present and not equal to ``n/a`` (can be customized). If ``text_pc`` is
    not available, it  will populate ``text`` from ``text_pc_pred`` field,
    following the same rules. If both are not available, it will fall back to
    the ``text`` field itself. In all cases it will specify which source was
    used in the ``text_origin`` field by using the label from the
    ``origin_label`` field.. If non of the sources is available,
    it will populate both the target and the origin fields with ``n/a``.

    Args:
        sources (list[dict]): list of the sources to use in order of preference.
            Each element in the list should be in the following format::

                {
                    field: <which field to take the data from>
                    origin_label: <what to write in the "<target>_origin"
                }
        target (str): target field that we are populating.
        na_indicator (str): if any source field has text equal to the
            ``na_indicator`` it will be considered as not available. If none
            of the sources are present, this will also be used as the value
            for the target and origin fields. Defaults to ``n/a``.

    Returns:
        The same data as in the input manifest enhanced with the following fields::

            <target>: <populated with data from either <source1> or <source2> \
                       or with <na_indicator> if none are available>
            <target>_origin: <label that marks where the data came from>
    """

    def __init__(
        self,
        sources: List[Dict[str, str]],
        target: str,
        na_indicator: str = "n/a",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.sources = sources
        self.target = target
        self.na_indicator = na_indicator

    def process_dataset_entry(self, data_entry: Dict):
        for source_dict in self.sources:
            if data_entry.get(source_dict["field"], self.na_indicator) != self.na_indicator:
                data_entry[self.target] = data_entry[source_dict["field"]]
                data_entry[f"{self.target}_origin"] = source_dict["origin_label"]
                break  # breaking out on the first present label
        else:  # going here if no break was triggered
            data_entry[self.target] = self.na_indicator
            data_entry[f"{self.target}_origin"] = self.na_indicator

        return [DataEntry(data=data_entry)]


class AddConstantFields(BaseParallelProcessor):
    """
    This processor adds constant fields to all manifest entries using Dask BaseParallelProcessor.
    It is useful when you want to attach fixed information (e.g., a language label or metadata)
    to each entry for downstream tasks such as language identification model training.

    Args:
        fields (dict): A dictionary containing key-value pairs of fields to add to each manifest entry.
            For example::

                {
                    "label": "en",
                    "metadata": "mcv-11.0-2022-09-21"
                }

    Returns:
        dict: The same data as in the input manifest with the added constant fields as specified in
        the ``fields`` dictionary.

    Example:

        .. code-block:: yaml

            - _target_: sdp.processors.modify_manifest.common.AddConstantFields
              input_manifest_file: ${workspace_dir}/input_manifest.json
              output_manifest_file: ${workspace_dir}/output_manifest.json
              fields:
                label: "en"
                metadata: "mcv-11.0-2022-09-21"
    """

    def __init__(self, fields: Dict, **kwargs):
        super().__init__(**kwargs)
        self.fields = fields

    def process_dataset_entry(self, data_entry: Dict):
        data_entry.update(self.fields)
        return [DataEntry(data=data_entry)]


class DuplicateFields(BaseParallelProcessor):
    """This processor duplicates fields in all manifest entries.

    It is useful for when you want to do downstream processing of a variant
    of the entry. E.g. make a copy of "text" called "text_no_pc", and
    remove punctuation from "text_no_pc" in downstream processors.

    Args:
        duplicate_fields (dict): dictionary where keys are the original
            fields to be copied and their values are the new names of
            the duplicate fields.

    Returns:
        The same data as in the input manifest with duplicated fields
        as specified in the ``duplicate_fields`` input dictionary.

    Example:
        .. code-block:: yaml

            - _target_: sdp.processors.modify_manifest.common.DuplicateFields
              input_manifest_file: ${workspace_dir}/test1.json
              output_manifest_file: ${workspace_dir}/test2.json
              duplicate_fields: {"text":"answer"}

    """

    def __init__(
        self,
        duplicate_fields: Dict,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.duplicate_fields = duplicate_fields

    def process_dataset_entry(self, data_entry: Dict):
        for field_src, field_tgt in self.duplicate_fields.items():
            if not field_src in data_entry:
                raise ValueError(f"Expected field {field_src} in data_entry {data_entry} but there isn't one.")

            data_entry[field_tgt] = data_entry[field_src]

        return [DataEntry(data=data_entry)]


class RenameFields(BaseParallelProcessor):
    """This processor renames fields in all manifest entries.

    Args:
        rename_fields: dictionary where keys are the fields to be
            renamed and their values are the new names of the fields.

    Returns:
        The same data as in the input manifest with renamed fields
        as specified in the ``rename_fields`` input dictionary.
    """

    def __init__(
        self,
        rename_fields: Dict,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.rename_fields = rename_fields

    def process_dataset_entry(self, data_entry: Dict):
        for field_src, field_tgt in self.rename_fields.items():
            if not field_src in data_entry:
                raise ValueError(f"Expected field {field_src} in data_entry {data_entry} but there isn't one.")

            data_entry[field_tgt] = data_entry[field_src]
            del data_entry[field_src]

        return [DataEntry(data=data_entry)]


class SplitOnFixedDuration(BaseParallelProcessor):
    """This processor splits audio into a fixed length segments.

    It does not actually create different audio files, but simply adds
    corresponding ``offset`` and ``duration`` fields. These fields can
    be automatically processed by NeMo to split audio on the fly during
    training.

    Args:
        segment_duration (float): fixed desired duration of each segment.
        drop_last (bool): whether to drop the last segment if total duration is
            not divisible by desired segment duration. If False, the last
            segment will be of a different length which is ``< segment_duration``.
            Defaults to True.
        drop_text (bool): whether to drop text from entries as it is most likely
            inaccurate after the split on duration. Defaults to True.

    Returns:
        The same data as in the input manifest but all audio that's longer
        than the ``segment_duration`` will be duplicated multiple times with
        additional ``offset`` and ``duration`` fields. If ``drop_text=True``
        will also drop ``text`` field from all entries.
    """

    def __init__(
        self,
        segment_duration: float,
        drop_last: bool = True,
        drop_text: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.segment_duration = segment_duration
        self.drop_last = drop_last
        self.drop_text = drop_text

    def process_dataset_entry(self, data_entry: Dict):
        total_duration = data_entry["duration"]
        total_segments = int(total_duration // self.segment_duration)
        output = [None] * total_segments
        for segment_idx in range(total_segments):
            modified_entry = data_entry.copy()  # shallow copy should be good enough
            modified_entry["duration"] = self.segment_duration
            modified_entry["offset"] = segment_idx * self.segment_duration
            if self.drop_text:
                modified_entry.pop("text", None)
            output[segment_idx] = DataEntry(data=modified_entry)

        remainder = total_duration - self.segment_duration * total_segments
        if not self.drop_last and remainder > 0:
            modified_entry = data_entry.copy()
            modified_entry["duration"] = remainder
            modified_entry["offset"] = self.segment_duration * total_segments
            if self.drop_text:
                modified_entry.pop("text", None)
            output.append(DataEntry(data=modified_entry))

        return output


class ChangeToRelativePath(BaseParallelProcessor):
    """This processor changes the audio filepaths to be relative.

    Args:
        base_dir: typically a folder where manifest file is going to be
            stored. All passes will be relative to that folder.

    Returns:
         The same data as in the input manifest with ``audio_filepath`` key
         changed to contain relative path to the ``base_dir``.
    """

    def __init__(
        self,
        base_dir: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.base_dir = base_dir

    def process_dataset_entry(self, data_entry: Dict):
        data_entry["audio_filepath"] = os.path.relpath(data_entry["audio_filepath"], self.base_dir)

        return [DataEntry(data=data_entry)]


class SortManifest(BaseProcessor):
    """Processor which will sort the manifest by some specified attribute.

    Args:
        attribute_sort_by (str): the attribute by which the manifest will be sorted.
        descending (bool): if set to False, attribute will be in ascending order.
            If True, attribute will be in descending order. Defaults to True.

    Returns:
        The same entries as in the input manifest, but sorted based
        on the provided parameters.
    """

    def __init__(
        self,
        attribute_sort_by: str,
        descending: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.attribute_sort_by = attribute_sort_by
        self.descending = descending

    def process(self):
        with open(self.input_manifest_file, "rt", encoding="utf8") as fin:
            dataset_entries = [json.loads(line) for line in fin.readlines()]

        dataset_entries = sorted(dataset_entries, key=lambda x: x[self.attribute_sort_by], reverse=self.descending)

        with open(self.output_manifest_file, "wt", encoding="utf8") as fout:
            for line in dataset_entries:
                fout.write(json.dumps(line, ensure_ascii=False) + "\n")


class KeepOnlySpecifiedFields(BaseProcessor):
    """Saves a copy of a manifest but only with a subset of the fields.

    Typically will be the final processor to save only relevant fields
    in the desired location.

    Args:
        fields_to_keep (list[str]): list of the fields in the input manifest
            that we want to retain. The output file will only contain these
            fields.

    Returns:
        The same data as in input manifest, but re-saved in the new location
        with only ``fields_to_keep`` fields retained.
    """

    def __init__(self, fields_to_keep: List[str], **kwargs):
        super().__init__(**kwargs)
        self.fields_to_keep = fields_to_keep

    def process(self):
        with open(self.input_manifest_file, "rt", encoding="utf8") as fin, open(
            self.output_manifest_file, "wt", encoding="utf8"
        ) as fout:
            for line in tqdm(fin):
                line = json.loads(line)
                new_line = {field: line[field] for field in self.fields_to_keep}
                fout.write(json.dumps(new_line, ensure_ascii=False) + "\n")


class ApplyInnerJoin(BaseProcessor):
    """Applies inner join to two manifests, i.e. creates a manifest from records that have matching values in both manifests.
    For more information, please refer to the Pandas merge function documentation:
    https://pandas.pydata.org/docs/reference/api/pandas.merge.html#pandas.merge


    Args:
        column_id (Union[str, List[str], None]): Field names to join on. These must be found in both manifests.
            If `column_id` is None then this defaults to the intersection of the columns in both manifests.
            Defaults to None.
        left_manifest_file (Optional[str]): path to the left manifest. Defaults to `input_manifest_file`.
        right_manifest_file (str): path to the right manifest.

    Returns:
        Inner join of two manifests.
    """

    def __init__(
        self,
        right_manifest_file: str,
        left_manifest_file: Optional[str] = None,
        column_id: Union[str, List[str], None] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.left_manifest_file = left_manifest_file if left_manifest_file != None else self.input_manifest_file
        self.right_manifest_file = right_manifest_file
        self.column_id = column_id

    def process(self):
        m1 = pd.DataFrame.from_records(load_manifest(Path(self.left_manifest_file)))
        m2 = pd.DataFrame.from_records(load_manifest(Path(self.right_manifest_file)))
        m3 = pd.merge(m1, m2, on=self.column_id, how="inner")

        with open(self.output_manifest_file, "wt", encoding="utf8") as fout:
            for _, line in m3.iterrows():
                fout.write(json.dumps(dict(line), ensure_ascii=False) + "\n")


class DropSpecifiedFields(BaseProcessor):
    """
    A processor that removes specified fields from each data entry in the manifest.

    This processor reads an input manifest line by line, drops the fields listed in `fields_to_drop` 
    from each JSON entry, and writes the cleaned entries to the output manifest.

    Args:
        fields_to_drop (List[str]): A list of keys to remove from each manifest entry.
        **kwargs: Additional arguments passed to the BaseProcessor (e.g., input/output manifest paths).

    Returns:
        A line-delimited JSON manifest, where each entry is the same as the input,
        but with the specified fields removed.
    """

    def __init__(self, fields_to_drop: List[str], **kwargs):
        super().__init__(**kwargs)
        self.fields_to_drop = fields_to_drop

    def process(self):
        # Open the input and output manifest files
        with open(self.input_manifest_file, "rt", encoding="utf8") as fin, open(
            self.output_manifest_file, "wt", encoding="utf8"
        ) as fout:
            # Iterate over each line (entry) in the input manifest
            for line in tqdm(fin):
                # Parse JSON entry from the current line
                entry = json.loads(line)
                # Create a new entry by excluding the specified fields
                new_line = {field: entry[field] for field in entry if field not in self.fields_to_drop}
                # Write the cleaned entry to the output manifest
                fout.write(json.dumps(new_line, ensure_ascii=False) + "\n")