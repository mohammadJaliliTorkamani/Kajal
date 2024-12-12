import constants
import utils
from pipeline import Pipeline


def main():
    input_dataset, input_error_message, fsl_dataset, fsl_error_message = utils.load_datasets(constants.INPUT_DATA_PATH,
                                                                                             constants.FSL_DATA_PATH)
    assert input_dataset, "Error while reading the input dataset file." + str(input_error_message)
    assert fsl_dataset, "Error while reading the input dataset file." + str(fsl_error_message)

    pipeline = Pipeline(input_dataset, fsl_dataset)
    raw_output = pipeline.run()
    results = pipeline.analyze(raw_output)
    utils.save_json(constants.PIPELINE_OUTPUT_PATH, results)


if __name__ == '__main__':
    main()
