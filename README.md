# Metrics for Simultaneous Subtitling
This repository contains the code for the evaluation of Simultaneous Speech Translation systems for Subtitling.

For further details, please refer to the paper: [Simultaneous Speech Translation for Live
Subtitling: from Delay to Display](https://arxiv.org/pdf/2107.08807.pdf)

## Metrics

- sacreBLEU
- Average Lagging
- Length Conformity
- Reading Speed ✨new✨

## Setup
The following software is required:
- [SimulEval](https://github.com/facebookresearch/SimulEval)
- Python version: 3.8.6

Download this repository:
```sh
git clone https://github.com/sarapapi/reading_speed
cd reading_speed
```

## Quick Start
To replicate our evaluation pipeline, first use the SimulEval tool to generate the output files (`instances.log` and `scores.log`).

The script run for the evaluation with SimulEval is the following:
```sh
simuleval \
    --agent ${FAIRSEQ_REPOSITORY}/examples/speech_to_text/simultaneous_translation/agents/fairseq_simul_st_agent.py \
    --source ${SRC_LIST_OF_AUDIO} \
    --target ${TGT_FILE} \
    --data-bin ${DATA_DIR} \
    --config ${CONFIG_YAML} \
    --model-path ${MODEL_DIR}/checkpoint_best.pt \
    --output ${GENERATE_OUTPUT_FOLDER} \
    --port {PORT_NUMBER} \
    --scores \
    --force-finish
```
where the `DATA_DIR` contains the dataset files (MuST-Cinema in our case), `CONFIG_YAML` is the .yaml file (see [Fairseq S2T](https://github.com/pytorch/fairseq/tree/master/examples/speech_to_text) documentation for the details), `TGT_FILE` contains the target (`amara.${LANG}` in our case, with `LANG={"it","de","fr"}`), and `SRC_LIST_OF_AUDIO` is the source audio lists obtained running the `audiosegmenter.py` script as follows:
```sh
python audiosegmenter.py --data-root ${DATA_DIR} --split-yaml ${CONFIG_YAML}
```

### sacreBLEU and Average Lagging
SimulEval `scores.log` file will be similar to:
```
{
    "Quality": {
        "BLEU": 27.86165803632365
    },
    "Latency": {
        "AL": 1935.6462250455804,
        "AL_CA": 2681.4577452773347,
        "AP": 0.7889193598010125,
        "AP_CA": 1.0965755087520004,
        "DAL": 2110.2846782719325,
        "DAL_CA": 3308.2131380973606
    }
}
```
`BLEU` represents the **sacreBLEU** score, and `AL` represents the **Average Lagging**.

### Length Conformity
The length conformity can be computed by running:
```sh
python reading_speed_scrollingwords.py ${K_VALUE} ${INSTANCES_PATH}
```
The output prompted will be similar to:
```
- CONFORMITY -
Correct length: 1204 (0.9107413010590015%)
Too_long (> 43): 98 (0.07413010590015129%) - Average length: 8.5
Too_short (< 6): 20 (0.015128593040847202%) - Average length: 4.4
```
where the first percentage (e.g. `0.9107413010590015%`) represents the **Conformity Length** metric.

### Reading Speed
The reading speed (rs) metric can be computed, for each type of visualization mode, as follows:
- **word-for-word**: ```python reading_speed_scrollingwords.py ${K_VALUE} ${INSTANCES_PATH}```
- **blocks**: ```python reading_speed_blocks.py ${K_VALUE} ${INSTANCES_PATH}```
- **scrolling lines**: ```python reading_speed_scrollinglines.py ${K_VALUE} ${INSTANCES_PATH}```
where `K_VALUE` is the wait-k step value, and `INSTANCES_PATH` is the path where `instances.log` SimulEval output file is located.
The output prompted will be similar to:
```
- READING SPEED -
Duration (mean and stdev): 5056.591594384641 +/- 4307.528791719213
Reading_speed (mean and stdev): 53.52209742804699 +/- 9.905798307633066
Percentage of subtitles respecting reading speed (rs < 21.01s): 0.6122448979591837
```
where the `Reading_speed` represents the **Reading Speed (rs)** metric.

## Citation
Please cite as:
```
@article{karakanta2021simultaneous,
  title={Simultaneous Speech Translation for Live Subtitling: from Delay to Display},
  author={Karakanta, Alina and Papi, Sara and Negri, Matteo and Turchi, Marco},
  journal={arXiv preprint arXiv:2107.08807},
  year={2021}
}
```
