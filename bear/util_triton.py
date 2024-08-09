import json
import numpy as np
from tritonclient.utils import np_to_triton_dtype
import tritonclient.grpc as grpcclient
from ast import literal_eval


class OfflineSpeechClient(object):

    def __init__(self, triton_client, model_name, protocol_client):
        self.triton_client = triton_client
        self.protocol_client = protocol_client
        self.model_name = model_name
        self.wav_fp = ''

    def recognize(self, waveform, data, idx=0):
        samples = np.array([waveform], dtype=np.float32)
        lengths = np.array([[len(waveform)]], dtype=np.int32)
        input_json = np.array([[json.dumps(data)]], dtype=np.string_)

        if data:
            input_json = np.array([[json.dumps(data)]], dtype=np.string_)
            inputs = [
                self.protocol_client.InferInput("WAV", samples.shape,
                                                np_to_triton_dtype(samples.dtype)),
                self.protocol_client.InferInput("WAV_LENS", lengths.shape,
                                                np_to_triton_dtype(lengths.dtype)),
                self.protocol_client.InferInput("INPUT_JSON", input_json.shape,
                                                np_to_triton_dtype(input_json.dtype)),
            ]
            inputs[0].set_data_from_numpy(samples)
            inputs[1].set_data_from_numpy(lengths)
            inputs[2].set_data_from_numpy(input_json)
        else:
            inputs = [
                self.protocol_client.InferInput("WAV", samples.shape,
                                                np_to_triton_dtype(samples.dtype)),
                self.protocol_client.InferInput("WAV_LENS", lengths.shape,
                                                np_to_triton_dtype(lengths.dtype)),
            ]
            inputs[0].set_data_from_numpy(samples)
            inputs[1].set_data_from_numpy(lengths)

        sequence_id = 10086 + idx

        if ('fea_enc_raw_' in self.model_name):

            outputs = [
                self.protocol_client.InferRequestedOutput("BEAM_LOG_PROBS"),
                self.protocol_client.InferRequestedOutput("BEAM_LOG_PROBS_IDX")
            ]
            response = self.triton_client.infer(
                self.model_name,
                inputs,
                request_id=str(sequence_id),
                outputs=outputs,
            )
            cur_b_log_probs = response.as_numpy("BEAM_LOG_PROBS")
            cur_b_log_probs_idx = response.as_numpy("BEAM_LOG_PROBS_IDX")

            return cur_b_log_probs, cur_b_log_probs_idx

        elif self.model_name == 'fea_enc_json':

            outputs = [
                self.protocol_client.InferRequestedOutput("BEAM_LOG_PROBS"),
                self.protocol_client.InferRequestedOutput("BEAM_LOG_PROBS_IDX"),
                self.protocol_client.InferRequestedOutput("INPUT_JSON")
            ]
            response = self.triton_client.infer(
                self.model_name,
                inputs,
                request_id=str(sequence_id),
                outputs=outputs,
            )

            cur_b_log_probs = response.as_numpy("BEAM_LOG_PROBS")
            cur_b_log_probs_idx = response.as_numpy("BEAM_LOG_PROBS_IDX")
            input_json = response.as_numpy("INPUT_JSON")

            return cur_b_log_probs, cur_b_log_probs_idx, input_json

        elif (self.model_name == 'asr_pipline'):

            outputs = [
                self.protocol_client.InferRequestedOutput("TRANSCRIPTS"),
                self.protocol_client.InferRequestedOutput("OUTPUT_JSON")
            ]
            response = self.triton_client.infer(
                self.model_name,
                inputs,
                request_id=str(sequence_id),
                outputs=outputs,
            )
            decoding_results0 = response.as_numpy("TRANSCRIPTS")[0]
            if type(decoding_results0) == np.ndarray:
                result0 = b" ".join(decoding_results0).decode("utf-8")
            else:
                result0 = decoding_results0.decode("utf-8")

            decoding_results1 = response.as_numpy("OUTPUT_JSON")[0]
            if type(decoding_results1) == np.ndarray:
                result1 = b" ".join(decoding_results1).decode("utf-8")
            else:
                result1 = decoding_results1.decode("utf-8")

            result1 = literal_eval(result1)
            return result0, result1


def single_job_OfflineSpeechClient(waveform, data='', url='0.0.0.0:8000', verbose=False, model_name='fea_enc_json', wav_fp=''):
    with grpcclient.InferenceServerClient(
            url=url, verbose=verbose) as triton_client:
        protocol_client = grpcclient
        speech_client_cls = OfflineSpeechClient
        speech_client = speech_client_cls(triton_client, model_name,
                                          protocol_client)
        speech_client.wav_fp = wav_fp
        result = speech_client.recognize(waveform, data)
    return result


class SpeechTokenizerClient(object):

    def __init__(self, triton_client, protocol_client):
        self.triton_client = triton_client
        self.protocol_client = protocol_client
        self.model_name = 'speech_tokenizer'

    def recognize(self, featutre, idx=0):
        feat = featutre
        feats_length = np.array([feat.shape[2]], dtype=np.int32)
        sequence_id = 10086 + idx

        inputs = [
            self.protocol_client.InferInput("feats", feat.shape,
                                            np_to_triton_dtype(feat.dtype)),
            self.protocol_client.InferInput("feats_length", feats_length.shape,
                                            np_to_triton_dtype(feats_length.dtype)),
        ]
        inputs[0].set_data_from_numpy(feat)
        inputs[1].set_data_from_numpy(feats_length)

        outputs = [
            self.protocol_client.InferRequestedOutput("indices"),
        ]

        response = self.triton_client.infer(
            self.model_name,
            inputs,
            request_id=str(sequence_id),
            outputs=outputs,
        )

        results = response.as_numpy("indices")
        return results


def single_job_SpeechTokenizerClient(feature, url, verbose=False):
    with grpcclient.InferenceServerClient(
            url=url, verbose=verbose) as triton_client:
        protocol_client = grpcclient
        speech_client_cls = SpeechTokenizerClient
        speech_tokenizer_client = speech_client_cls(triton_client, protocol_client)
        result = speech_tokenizer_client.recognize(feature)
    return result
