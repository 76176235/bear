import os
import subprocess
import tempfile


def dexec(args, input_data=None, needs_output=True):
    stdin = None if input_data is None else subprocess.PIPE
    stdout = None if not needs_output else subprocess.PIPE
    # log.v('exec', args)
    p = subprocess.Popen(
        args,
        stdin=stdin,
        stdout=stdout,
        stderr=subprocess.PIPE)
    out, error = p.communicate(input=input_data)

    if needs_output:
        return p.returncode, out, error
    else:
        return p.returncode, error


def _is_iter(o):
    if o is None or isinstance(o, str):
        return False
    try:
        _ = iter(o)
        return True
    except TypeError:
        return False


def _prepare_input(input_data, input_args):
    if input_data is None and input_args is None:
        return None, None, None, None
    if input_data is None:
        return None, None, input_args if _is_iter(input_args) else [
                                                  input_args], None
    if input_args is None:
        return subprocess.PIPE, input_data, None, None

    if not _is_iter(input_args):
        input_args = [input_args]
    if len(input_args) < 2:
        input_file = tempfile.NamedTemporaryFile()
        input_file.write(input_data)
        input_args.append(input_file.name)
        return None, None, input_args, input_file
    else:
        if not os.path.exists(input_args[1]):
            input_file = open(input_args[1], 'wb')
            input_file.write(input_data)
            input_file.close()
        return None, None, input_args, None


def _prepare_output(output_args, needs_output):
    if output_args is None and needs_output is None:
        return None, None, None
    if output_args is None:
        return subprocess.PIPE, None, None

    if not _is_iter(output_args):
        output_args = [output_args]

    if len(output_args) < 2:
        output_file = tempfile.NamedTemporaryFile()
        output_args.append(output_file.name)
        return None, output_args, output_file
    else:
        return None, output_args, None


def fexec(args, input_data=None, input_args=None,
          output_args=None, needs_output=False):

    stdin, input_data, input_args, temp_in = _prepare_input(
        input_data, input_args)
    stdout, output_args, temp_out = _prepare_output(output_args, needs_output)
    if _is_iter(output_args) and len(
            output_args) > 1 and not os.path.exists(output_args[1]):
        dir_path = os.path.split(output_args[1])[0]
        if len(dir_path) > 0:
            os.makedirs(dir_path, exist_ok=True)

    if input_args is not None:
        args.extend(input_args)
    if output_args is not None:
        args.extend(output_args)

    # log.v('fexec', args)
    p = subprocess.Popen(
        args,
        stdin=stdin,
        stdout=stdout,
        stderr=subprocess.PIPE)

    out, error = p.communicate(input=input_data)

    if temp_in:
        temp_in.close()
    if error:
        error = error.decode('utf-8')
    if needs_output:
        if p.returncode == 0 and needs_output and stdout is None:
            if temp_out is None:
                out = open(output_args[1], 'rb').read()
            else:
                out = temp_out.read()
                temp_out.close()
        return p.returncode, out, error
    else:
        return p.returncode, error
