import sys
import os
from argparse import ArgumentParser


def construct_line(line, data):
    """
    line: input line from original conllu, in the list form
    data: list with word attributes from the changes data structure

    Updates the input line list based on the info from the data list
    Returns: updated input line as a tab-separated string
    """
    assert line[1] == data[1]
    if len(data[5]) > 0:    # Update UPOS
        line[3] = data[5]
    else:
        assert line[3] == data[2]
    if len(data[6]) > 0:    # Update XPOS
        line[4] = data[6]
    else:
        assert line[4] == data[3]
    if len(data[7]) > 0:    # Update feats
        line[5] = data[7]
    else:
        assert line[5] == data[4]
    return '\t'.join(line)


def fix_conllu(in_fn, out_fn, changes):
    """
    Reads from the in_fn, finds docs/sentences/words from changes data structure
    whose annotation needs to be fixed,
    and writes the fixed data into out_fn.
    """
    with open(in_fn) as f:
        lines = f.readlines()

    doc_name = os.path.split(in_fn)[-1]
    with open(out_fn, 'w') as f:
        for line in lines:
            if line.startswith("# newdoc"):     # copy comment from input
                print(line.strip(), file=f)
            elif line.startswith("# sent_id"):  # copy comment from input
                sent_id = line.split('=')[1].strip()
                print(line.strip(), file=f)
            elif line.startswith("# text"):     # copy comment from input
                text = line.split('=')[1].strip()

                # ensure that the texts in the input file and and changes data structure match exactly
                if doc_name in changes and sent_id in changes[doc_name]:
                    assert changes[doc_name][sent_id]["text"] == text
                print(line.strip(), file=f)
            elif len(line.strip().split()) == 10:   # This is not a comment line
                data = line.strip().split()
                ind = data[0]
                # Check if the word annotation needs to be fixed
                if doc_name in changes and sent_id in changes[doc_name] and ind in changes[doc_name][sent_id]["words"]:
                    new_line = construct_line(data, changes[doc_name][sent_id]["words"][ind])   # construct a new annotation
                    print(new_line, file=f)
                else:
                    print(line.strip(), file=f)     # no fix is necessary, copy from the input
            else:
                assert len(line.strip()) == 0   # if not comment line and no data line then must be empty line
                print(file=f)


def read_changes(fn):
    """ Read the changes to be made into a dictionary.
    The dictionary has the following format:
    {doc_name1: {sent_name1: {'text': sentence text,
                               'words': {word_id1: [list with word attributes],
                                        word_id2: [list with word attributes]
                                        }
                               }
                 }
    }
    The list with word attributes has 8 elements:
    word_id, the word itself, old UPOS, old XPOS, old feats, new UPOS, new XPOS, new feats

    A real fragment of this data structure looks like this:
    {'aja_ee199920_osa1_ud28.enhanced.conllu': {'aja_ee199920_446':
    {'text': 'Inglaste idee oli rajada vanasse angaari tehaseväljamüügi (factory outlet ingl k) tüüpi kauplus.',
    'words': {'9': ['9', 'factory', 'NOUN', 'S', 'Foreign=Yes', 'X', 'T', 'Foreign=Yes'],
              '10': ['10', 'outlet', 'NOUN', 'S', 'Foreign=Yes', 'X', 'T', 'Foreign=Yes']}}}}
    """
    changes = {}
    with open(fn) as f:
        lines = f.readlines()[1:]   # Skip the first line

    read_doc = True
    read_sent = False
    read_text = False
    read_word = False

    doc_name = ""
    sent_name = ""
    words = {}

    for i, line in enumerate(lines):
        data = lines[i].strip().split('\t')
        # print(data)
        # print(read_doc, read_sent, read_text, read_word)
        if read_doc:
            assert data[0].endswith("conllu")
            doc_name = data[0]
            if doc_name not in changes:
                changes[doc_name] = {}
            read_doc = False
            read_sent = True
        elif read_sent:
            sent_name = data[0]
            doc_part = '_'.join(sent_name.split("_")[:-1])
            assert doc_name.startswith(doc_part)
            changes[doc_name][sent_name] = {}
            read_sent = False
            read_text = True
        elif read_text:
            for j in range(1, len(data)):
                assert len(data[j]) == 0
            text = data[0]
            changes[doc_name][sent_name]['text'] = text
            read_text = False
            read_word = True
        elif read_word:
            if len(data[0]) == 0:
                for j in range(1, len(data)):
                    assert len(data[j]) == 0
                changes[doc_name][sent_name]['words'] = words
                words = {}
                read_word = False
                read_doc = True
            else:
                assert int(data[0])
                words[data[0]] = data
        # print(changes)
    assert len(words) > 0
    changes[doc_name][sent_name]['words'] = words

    return changes


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--data_dir", help="Location of the dir with initial files, e.g. UD2_8/Train")
    parser.add_argument("--output_dir", help="Dir path for the fixed files, e.g. UD2_8/Train_fix")
    parser.add_argument("--changes_fn", help="Path to the changes file, i.e. UD_XPOS_fixes_train.tsv")
    args = parser.parse_args()
    changes = read_changes(args.changes_fn)
    # print(changes['aja_ee200110_osa_10_ud28.enhanced.conllu'])
    # sys.exit(0)

    if not os.path.isdir(args.output_dir):
        os.mkdir(args.output_dir)

    for fn in os.listdir(args.data_dir):
        fn_path = os.path.join(args.data_dir, fn)
        out_fn = os.path.join(args.output_dir, fn)
        fix_conllu(fn_path, out_fn, changes)

