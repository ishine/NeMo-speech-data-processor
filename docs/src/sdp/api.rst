API
---

Available processors
~~~~~~~~~~~~~~~~~~~~

Here is the full list of all available processors and their supported arguments.

.. note::
    All SDP processors optionally accept ``input_manifest_file`` and
    ``output_manifest_file`` keys. See :ref:`Special fields <special_fields>` section
    for more details.

.. Using autodata everywhere to only have class name and docs and save on space


Dataset-specific processors
###########################

MCV
'''

.. autodata:: sdp.processors.CreateInitialManifestMCV
   :annotation:

MLS
'''

.. indexed in the adding_processors section with methods description
.. autodata:: sdp.processors.CreateInitialManifestMLS
   :annotation:
   :noindex:

.. autodata:: sdp.processors.RestorePCForMLS
   :annotation:

VoxPopuli
'''''''''

.. autodata:: sdp.processors.CreateInitialManifestVoxpopuli
   :annotation:

.. autodata:: sdp.processors.NormalizeFromNonPCTextVoxpopuli
   :annotation:

CORAAL
''''''

.. autodata:: sdp.processors.CreateInitialManifestCORAAL
   :annotation:

.. autodata:: sdp.processors.TrainDevTestSplitCORAAL
   :annotation:


Librispeech
'''''''''''

.. autodata:: sdp.processors.CreateInitialManifestLibrispeech
   :annotation:
   

SLR83
'''''

.. autodata:: sdp.processors.CreateInitialManifestSLR83
   :annotation:

.. autodata:: sdp.processors.CustomDataSplitSLR83
   :annotation:

MTEDx
'''

.. autodata:: sdp.processors.CreateInitialManifestMTEDX
   :annotation:

Coraa
'''

.. autodata:: sdp.processors.CreateInitialManifestCORAA
   :annotation:

.. TODO: Fisher config is not accessible - should we require moving everything to SDP
..       Probably need some policy on shat lives in main folder vs configs.
..       To control the number of processors we support.

FLEURS
''''''

.. autodata:: sdp.processors.CreateInitialManifestFleurs
   :annotation:

UzbekVoice
''''''''''
.. autodata:: sdp.processors.CreateInitialManifestUzbekvoice
   :annotation:

Earnings21/22
'''''''''''''

.. autodata:: sdp.processors.datasets.earnings.CreateInitialAudioAndManifest
   :annotation:

.. autodata:: sdp.processors.datasets.earnings.CreateFullAudioManifestEarnings21
   :annotation:

.. autodata:: sdp.processors.datasets.earnings.SpeakerSegmentedManifest
   :annotation:

.. autodata:: sdp.processors.datasets.earnings.CreateSentenceSegmentedManifest
   :annotation:

.. autodata:: sdp.processors.datasets.earnings.NeMoForcedAligner
   :annotation:

.. autodata:: sdp.processors.datasets.earnings.ApplyEarnings21Normalizations
   :annotation:


MASC
''''''

.. autodata:: sdp.processors.CreateInitialManifestMASC
   :annotation:

MediaSpeech
''''''''''''

.. autodata:: sdp.processors.CreateInitialManifestMediaSpeech
   :annotation:


HuggingFace Datasets
''''''''''''''''''''

.. autodata:: sdp.processors.CreateInitialManifestHuggingFace
   :annotation:


YTC Datasets
''''''''''''

.. autodata:: sdp.processors.datasets.ytc.create_initial_manifest.CreateInitialManifestYTC
   :annotation:


HiFiTTS-2
''''''''''''''''''''

.. autodata:: sdp.processors.DownloadHiFiTTS2
   :annotation:

.. autodata:: sdp.processors.RemovedFailedChapters
   :annotation:


Lhotse processors
#################

The following processors leverage `Lhotse`_, a speech data handling library that contains
data preparation recipes for 80+ publicly available datasets.
Lhotse has its own data manifest format that can be largely mapped into NeMo's format.

.. autodata:: sdp.processors.LhotseImport
    :annotation:


.. _Lhotse: https://github.com/lhotse-speech/lhotse

Data enrichment
###############

The following processors can be used to add additional attributes to the data by
running different NeMo models (e.g., ASR predictions). These attributes are typically
used in the downstream processing for additional enhancement or filtering.

.. autodata:: sdp.processors.ASRInference
   :annotation:

.. autodata:: sdp.processors.PCInference
   :annotation:

.. autodata:: sdp.processors.ASRTransformers
   :annotation:

.. autodata:: sdp.processors.EstimateBandwidth
   :annotation:

.. autodata:: sdp.processors.tts.pyannote.PyAnnoteDiarizationAndOverlapDetection
   :annotation:

.. autodata:: sdp.processors.tts.nemo_asr_align.NeMoASRAligner
   :annotation:

.. autodata:: sdp.processors.tts.text.InverseTextNormalizationProcessor
   :annotation:

.. autodata:: sdp.processors.tts.metrics.TorchSquimObjectiveQualityMetricsProcessor
   :annotation:

.. autodata:: sdp.processors.tts.metrics.BandwidthEstimationProcessor
   :annotation:

Text-only processors
####################

.. note::
    All processors in this section accept additional parameter
    ``text_key`` (defaults to "text") to control which field is used
    for modifications/filtering.

.. autodata:: sdp.processors.ReadTxtLines
   :annotation:

Data modifications
''''''''''''''''''

.. indexed in the adding_processors section with methods description

.. autodata:: sdp.processors.SubRegex
   :annotation:
   :noindex:

.. autodata:: sdp.processors.SubMakeLowercase
   :annotation:

.. autodata:: sdp.processors.MakeLettersUppercaseAfterPeriod
   :annotation:

.. autodata:: sdp.processors.SplitLineBySentence
   :annotation:

.. autodata:: sdp.processors.CountNumWords
   :annotation:

.. autodata:: sdp.processors.NormalizeText
   :annotation:
   
.. autodata:: sdp.processors.InverseNormalizeText
   :annotation:

.. autodata:: sdp.processors.LambdaExpression
   :annotation:
  
.. autodata:: sdp.processors.ListToEntries
   :annotation:

Data filtering
''''''''''''''

.. autodata:: sdp.processors.DropIfRegexMatch
   :annotation:

.. autodata:: sdp.processors.DropIfNoneOfRegexMatch
   :annotation:

.. autodata:: sdp.processors.DropNonAlphabet
   :annotation:

.. autodata:: sdp.processors.DropOnAttribute
   :annotation:


ASR-based processors
####################

.. note::
    All processors in this section depend on the :class:`sdp.processors.ASRInference`.
    So make sure to include it in the config at some prior stage with an applicable
    ASR model.

.. note::
    All processors in this section accept additional parameters
    ``text_key`` (defaults to "text") and ``pred_text_key`` (defaults to "text_pred")
    to control which fields contain transcription and ASR model predictions.

.. autodata:: sdp.utils.BootstrapProcessor
   :annotation:

Data modifications
''''''''''''''''''

.. autodata:: sdp.processors.InsIfASRInsertion
   :annotation:

.. autodata:: sdp.processors.SubIfASRSubstitution
   :annotation:

Files management
''''''''''''''''

.. autodata:: sdp.processors.SoxConvert
   :annotation:

.. autodata:: sdp.processors.FfmpegConvert
   :annotation:

.. autodata:: sdp.processors.ExtractTar
   :annotation:

.. autodata:: sdp.processors.RemoveFiles
   :annotation:

Data filtering
''''''''''''''

.. autodata:: sdp.processors.PreserveByValue
   :annotation:

.. autodata:: sdp.processors.DropASRError
   :annotation:

.. autodata:: sdp.processors.DropASRErrorBeginningEnd
   :annotation:

.. autodata:: sdp.processors.DropIfSubstringInInsertion
   :annotation:

.. autodata:: sdp.processors.DropHighCER
   :annotation:

.. autodata:: sdp.processors.DropHighWER
   :annotation:

.. autodata:: sdp.processors.DropLowWordMatchRate
   :annotation:

.. indexed in the adding_processors section with methods description
.. autodata:: sdp.processors.DropHighLowCharrate
   :annotation:
   :noindex:

.. autodata:: sdp.processors.DropHighLowWordrate
   :annotation:

.. autodata:: sdp.processors.DropHighLowDuration
   :annotation:

.. autodata:: sdp.processors.DropRepeatedFields
   :annotation:

.. autodata:: sdp.processors.DropDuplicates
   :annotation:

.. autodata:: sdp.processors.AcceptIfWERLess
    :annotation:

.. autodata:: sdp.processors.CreateTolokaPool
    :annotation:

.. autodata:: sdp.processors.CreateTolokaProject
    :annotation:

.. autodata:: sdp.processors.CreateSentenceSet
    :annotation:

.. autodata:: sdp.processors.CreateTolokaTaskSet
    :annotation:

.. autodata:: sdp.processors.GetTolokaResults
    :annotation:

.. autodata:: sdp.processors.RejectIfBanned
    :annotation:

Miscellaneous
#############

.. autodata:: sdp.processors.AddConstantFields
   :annotation:

.. autodata:: sdp.processors.CombineSources
   :annotation:

.. autodata:: sdp.processors.DuplicateFields
   :annotation:

.. autodata:: sdp.processors.RenameFields
   :annotation:

.. autodata:: sdp.processors.SplitOnFixedDuration
   :annotation:

.. autodata:: sdp.processors.ChangeToRelativePath
   :annotation:

.. autodata:: sdp.processors.SortManifest
   :annotation:

.. autodata:: sdp.processors.KeepOnlySpecifiedFields
   :annotation:

.. autodata:: sdp.processors.GetAudioDuration
   :annotation:

.. autodata:: sdp.processors.CreateInitialManifestByExt
   :annotation:

.. autodata:: sdp.processors.ApplyInnerJoin
   :annotation:

.. autodata:: sdp.processors.CreateCombinedManifests
   :annotation:

.. autodata:: sdp.processors.tts.split.SplitLongAudio
   :annotation:

.. autodata:: sdp.processors.tts.split.JoinSplitAudioMetadata
   :annotation:

.. autodata:: sdp.processors.tts.merge_alignment_diarization.MergeAlignmentDiarization
   :annotation:

.. autodata:: sdp.processors.tts.prepare_tts_segments.PrepareTTSSegmentsProcessor
   :annotation:

.. autodata:: sdp.processors.ipl.nemo_run_processor.NemoRunIPLProcessor
   :annotation:

.. autodata:: sdp.processors.ipl.ipl_processors.TrainingCommandGenerator
   :annotation:

.. autodata:: sdp.processors.ipl.ipl_processors.InferenceCommandGenerator
   :annotation:

.. autodata:: sdp.processors.DropSpecifiedFields
   :annotation:

.. _sdp-base-classes:

Base classes
~~~~~~~~~~~~

This section lists all the base classes you might need to know about if you
want to add new SDP processors.

BaseProcessor
#############

.. autoclass:: sdp.processors.base_processor.BaseProcessor
   :show-inheritance:
   :private-members:
   :member-order: bysource
   :exclude-members: _abc_impl

BaseParallelProcessor
#####################

.. autoclass:: sdp.processors.base_processor.BaseParallelProcessor
   :show-inheritance:
   :private-members:
   :member-order: bysource
   :exclude-members: _abc_impl

.. _sdp-runtime-tests:

Runtime tests
#############

Before running the specified processors, SDP runs ``processor.test()`` on all specified processors.
A test method is provided in :meth:`sdp.processors.base_processor.BaseParallelProcessor.test`, which
checks that for a given input data entry, the output data entry/entries produced by the processor
will match the expected output data entry/entries. Note that this essentially only checks that the
impact on the data manifest will be as expected. If you want to do some other checks, you will need
to override this `test` method.

The input data entry and the expected output data entry/entries for
:meth:`sdp.processors.base_processor.BaseParallelProcessor.test` are specified inside the optional list
of ``test_cases`` that were provided in the object constructor.
This means you can provided test cases in the YAML config file, and the
dataset will only be processed if the test cases pass.

This is helpful to (a) make sure that the rules you wrote have the effect
you desired, and (b) demonstrate why you wrote those rules.
An example of test cases we could include in the YAML config file::

    - _target_: sdp.processors.DropIfRegexMatch
    regex_patterns:
        - "(\\D ){5,20}" # looks for between 4 and 19 characters surrounded by spaces
    test_cases:
        - {input: {text: "some s p a c e d out letters"}, output: null}
        - {input: {text: "normal words only"}, output: {text: "normal words only"}}
