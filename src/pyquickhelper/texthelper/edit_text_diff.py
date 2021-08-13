# -*- coding: utf-8 -*-
"""
@file
@brief Improves text comparison.
"""
import numpy


def edit_distance_string(s1, s2):
    """
    Computes the edit distance between strings *s1* and *s2*.

    :param s1: first string
    :param s2: second string
    :return: dist, list of tuples of aligned characters
    """
    n1 = len(s1) + 1
    n2 = len(s2) + 1
    dist = numpy.full((n1, n2), n1 * n2, dtype=numpy.float64)
    pred = numpy.full(dist.shape, 0, dtype=numpy.int32)

    for i in range(0, n1):
        dist[i, 0] = i
        pred[i, 0] = 1
    for j in range(1, n2):
        dist[0, j] = j
        pred[0, j] = 2
    pred[0, 0] = -1

    for i in range(1, n1):
        for j in range(1, n2):
            c = dist[i, j]

            p = 0
            if dist[i - 1, j] + 1 < c:
                c = dist[i - 1, j] + 1
                p = 1
            if dist[i, j - 1] + 1 < c:
                c = dist[i, j - 1] + 1
                p = 2
            d = 0 if s1[i - 1] == s2[j - 1] else 1
            if dist[i - 1, j - 1] + d < c:
                c = dist[i - 1, j - 1] + d
                p = 3
            if p == 0:
                raise RuntimeError(
                    "Unexpected value for p=%d at position=%r." % (p, (i, j)))

            dist[i, j] = c
            pred[i, j] = p

    d = dist[len(s1), len(s2)]
    equals = []
    i, j = len(s1), len(s2)
    p = pred[i, j]
    while p != -1:
        if p == 3:
            equals.append((i - 1, j - 1))
            i -= 1
            j -= 1
        elif p == 2:
            j -= 1
        elif p == 1:
            i -= 1
        else:
            raise RuntimeError(
                "Unexpected value for p=%d at position=%r." % (p, (i, j)))
        p = pred[i, j]
    return d, list(reversed(equals))


def edit_distance_text(rows1, rows2, strategy="full", threshold=0.5,
                       verbose=False):
    """
    Computes an edit distance between lines of a text.

    :param rows1: first set of rows
    :param rows2: second set of rows
    :param strategy: strategy to match lines (see below)
    :param threshold: two lines can match if the edit distance is not too big,
        a low threshold means no match
    :param verbose: if True, show progress with tqdm
    :return: distance, list of tuples of aligned lines, distance and
        alignment for each aligned lines, and finally an array
        with aligned line number for both texts

    Strategies:
    * `'full'`: computes all edit distances between all lines
    """
    if strategy != 'full':
        raise NotImplementedError(  # pragma: no cover
            "No other strategy than 'full' was implemented.")
    cached_distances = {}

    def cost_insert(row):
        return len(row) * 0.49

    def cost_cmp(i, j, row1, row2, bypass=True):
        c1 = cost_insert(row1)
        c2 = cost_insert(row2)
        if bypass and min(c1, c2) < threshold * max(c1, c2):
            if len(row1) < len(row2):
                return cost_insert(row2[len(row1):])
            return cost_insert(row1[len(row2):])
        if (i, j) in cached_distances:
            return cached_distances[i, j][0]
        ed, equals = edit_distance_string(row1, row2)
        cached_distances[i, j] = ed, equals
        return ed

    if isinstance(rows1, str):
        rows1 = rows1.split("\n")
    if isinstance(rows2, str):
        rows2 = rows2.split("\n")

    n1 = len(rows1) + 1
    n2 = len(rows2) + 1
    t1 = sum(map(len, rows1)) + 1
    t2 = sum(map(len, rows2)) + 1
    dist = numpy.full((n1, n2), t1 * t2, dtype=numpy.float64)
    pred = numpy.full(dist.shape, 0, dtype=numpy.int32)

    dist[0, 0] = 0
    for i in range(1, n1):
        dist[i, 0] = cost_insert(rows1[i - 1])
        pred[i, 0] = 1
    for j in range(1, n2):
        dist[0, j] = cost_insert(rows2[j - 1])
        pred[0, j] = 2
    pred[0, 0] = -1

    if verbose:
        from tqdm import tqdm
        loop = tqdm(range(1, n1))
    else:
        loop = range(1, n1)
    for i in loop:
        for j in range(1, n2):
            c = dist[i, j]

            p = 0
            d = dist[i - 1, j] + cost_insert(rows1[i - 1])
            if d < c:
                c = d
                p = 1
            d = dist[i, j - 1] + cost_insert(rows2[j - 1])
            if d < c:
                c = d
                p = 2
            if c < dist[i - 1, j - 1]:
                dist[i, j] = c
                pred[i, j] = p
                continue
            d = dist[i - 1, j - 1] + \
                cost_cmp(i - 1, j - 1, rows1[i - 1], rows2[j - 1])
            if d < c:
                c = d
                p = 3
            if p == 0:
                raise RuntimeError(
                    "Unexpected value for p=%d at position=%r, c=%d, "
                    "dist[i, j]=%d, dist=\n%r." % (
                        p, (i, j), c, dist[i, j],
                        dist[i - 1:i + 1, j - 1: j + 1]))

            dist[i, j] = c
            pred[i, j] = p

    d = dist[n1 - 1, n2 - 1]
    equals = []
    i, j = n1 - 1, n2 - 1
    lines1 = {}
    lines2 = {}
    p = pred[i, j]
    while p != -1:
        if p == 3:
            if (i - 1, j - 1) not in cached_distances:
                cost_cmp(i - 1, j - 1, rows1[i - 1],
                         rows2[j - 1], bypass=False)
            cd = cached_distances[i - 1, j - 1]
            lines1[i - 1] = j - 1
            lines2[j - 1] = i - 1
            equals.append((i - 1, j - 1) + cd)
            i -= 1
            j -= 1
        elif p == 2:
            j -= 1
        elif p == 1:
            i -= 1
        else:
            raise RuntimeError(
                "Unexpected value for p=%d at position=%r." % (p, (i, j)))
        p = pred[i, j]

    # final alignment
    aligned = []
    la = 0
    lb = 0
    while la < len(rows1) or lb < len(rows2):
        if la in lines1 and lb in lines2:
            aligned.append((la, lb))
            la += 1
            lb += 1
        while la not in lines1 and la < len(rows1):
            aligned.append((la, None))
            la += 1
        while lb not in lines2 and lb < len(rows2):
            aligned.append((None, lb))
            lb += 1
    return d, list(reversed(equals)), aligned


def diff2html(rows1, rows2, equals, aligned):
    """
    Produces a HTML report with differences between *rows1*
    and *rows2*.

    :param rows1: first set of rows
    :param rows2: second set of rows
    :param equals: third output of @see fn edit_distance_text
    :param aligned: fourth output of @see fn edit_distance_text
    :return: HTML text
    """
    if isinstance(rows1, str):
        rows1 = rows1.split("\n")
    if isinstance(rows2, str):
        rows2 = rows2.split("\n")

    char_aligned = {}
    for i, j, d, eq in equals:
        char_aligned[i, j] = (d, eq)

    tr = '<tr style="1px solid black;">'
    tr_ = '</tr>'
    tda = '<td style="background-color:#E59866;"><code>'
    tda_ = '</code></td>'
    tdb = '<td style="background-color:#ABEBC6;"><code>'
    tdb_ = '</code></td>'
    tdc = '<td style="background-color:#E5E7E9;"><code>'
    tdc_ = '</code></td>'
    spana = '<span style="color:#BA4A00;">'
    spanb = '<span style="color:#196F3D;">'
    span_ = "</span>"
    rows = []
    rows.append(
        '<table style="white-space: pre; 1px solid black; font-family:courier; text-align:left !important;">')
    for a, b in aligned:
        row = [tr]
        if a is None:
            row.append("<td></td>")
        elif b is None:
            row.extend([tda, str(a), tda_])
        else:
            row.extend(["<td><code>", str(a), "</code></td>"])
        if b is None:
            row.append("<td></td>")
        elif a is None:
            row.extend([tdb, str(b), tdb_])
        else:
            row.extend(["<td><code>", str(b), "</code></td>"])
        if a is None:
            row.extend([tdb, rows2[b], tdb_])
        elif b is None:
            row.extend([tda, rows1[a], tda_])
        else:
            al = char_aligned[a, b]
            if al[0] == 0:
                row.extend(["<td><code>", rows1[a], "</code></td>"])
            else:
                # Not equal
                s1 = rows1[a]
                s2 = rows2[b]
                l1 = [spana + _ + span_ for _ in s1]
                l2 = [spanb + _ + span_ for _ in s2]
                for i, j in al[1]:
                    if i is None or j is None:
                        continue
                    if s1[i] == s2[j]:
                        l1[i] = s1[i]
                        l2[j] = s2[j]
                row.extend(
                    [tdc, "".join(l1), "</code><br /><code>", "".join(l2), tdc_])
        row.append(tr_)
        rows.append("".join(row))
    rows.append("</table>")
    return "\n".join(rows)
