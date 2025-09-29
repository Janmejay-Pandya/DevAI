THRESHOLD = 25

def is_overlapping_y(elm1, elm2):
    return not (elm1['ymax'] < elm2['ymin'] or elm2['ymax'] < elm1['ymin'])

def is_right_of(elm1, elm2):
    return elm1['xmin'] > elm2['xmax']

def build_structure(elements):
    layout = {"name": "container", "type": "row", "children": []}

    def wrap_in_column(elms):
        return {
            "name": "container",
            "type": "col",
            "children": elms
        }

    columns = []  # Each is a list of elements in a column

    for elm in elements:
        placed = False
        for col in columns:
            # Try to place in this column if left-aligned and vertically stacked
            last = col[-1]
            if abs(elm['xmin'] - last['xmin']) < THRESHOLD and elm['ymin'] >= last['ymax']:
                col.append(elm)
                placed = True
                break

        if not placed:
            # Try to place as a new column if it's to the right and overlaps in height
            for col in columns:
                if is_overlapping_y(col[0], elm) and is_right_of(elm, col[0]):
                    columns.append([elm])
                    placed = True
                    break

        if not placed:
            # Fallback: first element or far enough away, just start a new column
            columns.append([elm])

    layout['children'] = [wrap_in_column([{"type": e['name']} for e in col]) for col in columns]

    return layout



elements = [{'name': 'Heading', 'confidence': 0.5225816965103149, 'xmin': 115.06996154785156, 'ymin': 63.390316009521484, 'xmax': 231.96792602539062, 'ymax': 110.7850341796875}, {'name': 'Image', 'confidence': 0.7342765927314758, 'xmin': 495.1536560058594, 'ymin': 107.40408325195312, 'xmax': 814.3570556640625, 'ymax': 366.48944091796875}, {'name': 'Heading', 'confidence': 0.5582699179649353, 'xmin': 120.1803207397461, 'ymin': 144.8352813720703, 'xmax': 202.1673583984375, 'ymax': 184.91189575195312}, {'name': 'Paragraph', 'confidence': 0.936739444732666, 'xmin': 117.89310455322266, 'ymin': 196.598876953125, 'xmax': 436.0515441894531, 'ymax': 340.5019226074219}, {'name': 'Heading', 'confidence': 0.6314518451690674, 'xmin': 108.67418670654297, 'ymin': 380.7641906738281, 'xmax': 198.72662353515625, 'ymax': 421.2037658691406}, {'name': 'Label', 'confidence': 0.4641669988632202, 'xmin': 109.71687316894531, 'ymin': 384.0714416503906, 'xmax': 201.3130340576172, 'ymax': 423.75823974609375}, {'name': 'Label', 'confidence': 0.804358720779419, 'xmin': 499.03704833984375, 'ymin': 414.585205078125, 'xmax': 571.445068359375, 'ymax': 455.54864501953125}, {'name': 'Image', 'confidence': 0.9401587247848511, 'xmin': 104.78716278076172, 'ymin': 445.9580383300781, 'xmax': 215.9578094482422, 'ymax': 596.84814453125}, {'name': 'Label', 'confidence': 0.6549487113952637, 'xmin': 224.8734893798828, 'ymin': 458.2862243652344, 'xmax': 394.1216735839844, 'ymax': 503.3916320800781}, {'name': 'Image', 'confidence': 0.9389886260032654, 'xmin': 481.58526611328125, 'ymin': 474.5577392578125, 'xmax': 585.8043212890625, 'ymax': 625.3919677734375}, {'name': 'Label', 'confidence': 0.7828032374382019, 'xmin': 598.5488891601562, 'ymin': 488.0311584472656, 'xmax': 755.2236938476562, 'ymax': 528.7913208007812}, {'name': 'Label', 'confidence': 0.5979044437408447, 'xmin': 607.8603515625, 'ymin': 488.44354248046875, 'xmax': 683.48828125, 'ymax': 524.0587158203125}, {'name': 'Label', 'confidence': 0.2803417146205902, 'xmin': 689.2648315429688, 'ymin': 490.3867492675781, 'xmax': 762.4995727539062, 'ymax': 531.8699951171875}, {'name': 'Paragraph', 'confidence': 0.911799967288971, 'xmin': 221.2897186279297, 'ymin': 506.9870910644531, 'xmax': 376.8894348144531, 'ymax': 600.7537841796875}, {'name': 'Paragraph', 'confidence': 0.9183638691902161, 'xmin': 597.0318603515625, 'ymin': 525.4249267578125, 'xmax': 754.5653076171875, 'ymax': 630.1327514648438}, {'name': 'Label', 'confidence': 0.638762891292572, 'xmin': 108.42449951171875, 'ymin': 690.6016235351562, 'xmax': 192.4778594970703, 'ymax': 727.4940795898438}, {'name': 'Label', 'confidence': 0.8164858818054199, 'xmin': 473.6148681640625, 'ymin': 709.150390625, 'xmax': 562.2332153320312, 'ymax': 750.8611450195312}, {'name': 'Image', 'confidence': 0.9253625869750977, 'xmin': 96.68402099609375, 'ymin': 763.0697631835938, 'xmax': 201.68238830566406, 'ymax': 889.5286865234375}, {'name': 'Label', 'confidence': 0.6912002563476562, 'xmin': 221.1282196044922, 'ymin': 764.1941528320312, 'xmax': 375.4440612792969, 'ymax': 806.6002807617188}, {'name': 'Image', 'confidence': 0.9334873557090759, 'xmin': 456.286376953125, 'ymin': 777.32177734375, 'xmax': 570.7240600585938, 'ymax': 917.6349487304688}, {'name': 'Paragraph', 'confidence': 0.9360595345497131, 'xmin': 207.06166076660156, 'ymin': 798.61865234375, 'xmax': 368.602783203125, 'ymax': 892.58447265625}, {'name': 'Label', 'confidence': 0.6695694923400879, 'xmin': 586.0039672851562, 'ymin': 786.4417114257812, 'xmax': 702.0406494140625, 'ymax': 827.6222534179688}, {'name': 'Label', 'confidence': 0.4603174328804016, 'xmin': 684.1143188476562, 'ymin': 790.375732421875, 'xmax': 743.1173095703125, 'ymax': 830.3889770507812}, {'name': 'Paragraph', 'confidence': 0.8457518219947815, 'xmin': 574.9850463867188, 'ymin': 828.9442749023438, 'xmax': 744.818115234375, 'ymax': 927.9679565429688}]

print(build_structure(elements))