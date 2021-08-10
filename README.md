# Metrics for Simultaneous Subtitling
This repository contains the code for the evaluation of Simultaneous Speech Translation systems for Subtitling.

For further details, please refer to the paper: [Simultaneous Speech Translation for Live
Subtitling: from Delay to Display](https://arxiv.org/pdf/2107.08807.pdf)

## Metrics

- sacreBLEU
- Average Lagging
- Length Conformity
- Subtitle Delay
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
python length.py ${K_VALUE} ${INSTANCES_PATH}
```
The output prompted will be similar to:
```
- CONFORMITY -
Correct length: 1204 (91.07%)
Too_long (> 43): 98 (7.41%) - Average length: 8.5
Too_short (< 6): 20 (1.51%) - Average length: 4.4
```
where the first percentage (e.g. `0.91%`) represents the **Conformity Length** metric.

### Reading Speed
The reading speed (rs) metric can be computed, for each type of visualization mode, as follows:
- **word-for-word**: ```python reading_speed_scrollingwords.py ${K_VALUE} ${INSTANCES_PATH}```
- **blocks**: ```python reading_speed_blocks.py ${K_VALUE} ${INSTANCES_PATH}```
- **scrolling lines**: ```python reading_speed_scrollinglines.py ${K_VALUE} ${INSTANCES_PATH}```
where `K_VALUE` is the wait-k step value, and `INSTANCES_PATH` is the path where `instances.log` SimulEval output file is located.
The output prompted will be similar to:
```
- READING SPEED -
Duration (mean and stdev): 2375.9 +/- 3060.96
Reading speed (mean and stdev): 53.35 +/- 9.91
Percentage of subtitles respecting reading speed (rs < 21.01s): 38.88%

- DELAY -
Subtitle delay: 4690.2 +/- 3380.11
```
where the `Reading speed` represents the **Reading Speed (rs)** metric and the `Subtitle delay` represents the **Delay**.


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
