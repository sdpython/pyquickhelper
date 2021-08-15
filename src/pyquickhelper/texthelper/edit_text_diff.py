# -*- coding: utf-8 -*-
"""
@file
@brief Improves text comparison.
"""
import numpy
try:
    from cpyquickhelper.algorithms.edit_distance import (
        edit_distance_string as edit_distance_string_fast)
except ImportError:
    edit_distance_string_fast = None


def edit_distance_string(s1, s2, cmp_cost=1.):
    """
    Computes the edit distance between strings *s1* and *s2*.

    :param s1: first string
    :param s2: second string
    :return: dist, list of tuples of aligned characters

    Another version is implemented in module :epkg:`cpyquickhelper`.
    It uses C++ to make it around 25 times faster than the python
    implementation.
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
            d = 0 if s1[i - 1] == s2[j - 1] else cmp_cost
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


def edit_distance_text(rows1, rows2, strategy="full",
                       verbose=False, return_matrices=False,
                       **thresholds):
    """
    Computes an edit distance between lines of a text.

    :param rows1: first set of rows
    :param rows2: second set of rows
    :param strategy: strategy to match lines (see below)
    :param verbose: if True, show progress with tqdm
    :param return_matrices: return distances and predecessor
        matrices as well
    :param thresholds: see below
    :return: distance, list of tuples of aligned lines, distance and
        alignment for each aligned lines, and finally an array
        with aligned line number for both texts

    Strategies:
    * `'full'`: computes all edit distances between all lines

    Thresholds:
    * `'threshold'`: two lines can match if the edit distance is not too big,
        a low threshold means no match (default is 0.5)
    * `'insert_len'`: variable cost of insertion (default is 1.)
    * `'insert_cst'`: fixed cost of insertion (default is 1.)
    * `'weight_cmp'`: weight for comparison cost (default is 2.)
    * '`cmp_cost'`: cost of a bad comparison, default is `2 * insert_len`

    .. note::

        The full python implementation is quite slow. Function
        @see fn edit_distance_string is also implemented in module
        :epkg:`cpyquickhelper`. If this module is installed and recent
        enough, this function will use this version as it is 25 times
        faster. The version in :epkg:`cpyquickhelper` is using C++.
    """
    if strategy != 'full':
        raise NotImplementedError(  # pragma: no cover
            "No other strategy than 'full' was implemented.")
    cached_distances = {}

    insert_len = thresholds.get('insert_len', 1.)
    insert_cst = thresholds.get('insert_cst', 1.)
    threshold = thresholds.get('threshold', 0.5)
    weight_cmp = thresholds.get('weight_cmp', 2.)
    cmp_cost = thresholds.get('cmp_cost', 2. * insert_len)

    fct_cmp = edit_distance_string_fast or edit_distance_string

    def cost_insert(row):
        s = row.strip("\t ")
        return (len(s) + insert_cst) * insert_len

    def cost_cmp(i, j, row1, row2, bypass=True):
        s1 = row1.strip('\t ')
        s2 = row2.strip('\t ')
        c1 = cost_insert(s1)
        c2 = cost_insert(s2)
        if (bypass and len(s1) > 9 and len(s2) > 9 and
                min(c1, c2) < threshold * max(c1, c2)):
            if len(row1) < len(row2):
                return cost_insert(row2[len(row1):]), []
            return cost_insert(row1[len(row2):]), []
        if (i, j) in cached_distances:
            return cached_distances[i, j]
        ed, equals = fct_cmp(row1, row2, cmp_cost=cmp_cost)
        ed *= weight_cmp
        cached_distances[i, j] = ed, equals
        return ed, equals

    if isinstance(rows1, str):
        rows1 = rows1.split("\n")
    if isinstance(rows2, str):
        rows2 = rows2.split("\n")

    n1 = len(rows1) + 1
    n2 = len(rows2) + 1
    t1 = sum(map(len, rows1)) + 1
    t2 = sum(map(len, rows2)) + 1
    dist = numpy.full((n1, n2), t1 * t2 + t1 + t2 + 10, dtype=numpy.float64)
    pred = numpy.full(dist.shape, 0, dtype=numpy.int32)

    dist[0, 0] = 0
    for i in range(1, n1):
        dist[i, 0] = cost_insert(rows1[i - 1]) + dist[i - 1, 0]
        pred[i, 0] = 1
    for j in range(1, n2):
        dist[0, j] = cost_insert(rows2[j - 1]) + dist[0, j - 1]
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
            d = (dist[i - 1, j - 1] +
                 cost_cmp(i - 1, j - 1, rows1[i - 1], rows2[j - 1])[0])
            if d < c:
                c = d
                p = 3
            if p == 0:
                print(i, j)
                print(dist)
                print(pred)
                raise RuntimeError(
                    "Unexpected value for p=%d at position=%r, c=%d, "
                    "dist[i, j]=%d, dist=\n%r." % (
                        p, (i, j), c, dist[i, j],
                        dist[i - 1:i + 1, j - 1: j + 1]))

            dist[i, j] = c
            pred[i, j] = p

    cached_distances.clear()
    d = dist[n1 - 1, n2 - 1]
    equals = []
    i, j = n1 - 1, n2 - 1
    lines1 = {}
    lines2 = {}
    p = pred[i, j]
    while p != -1:
        if p == 3:
            cd = cost_cmp(i - 1, j - 1, rows1[i - 1],
                          rows2[j - 1], bypass=False)
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
    if return_matrices:
        return d, list(reversed(equals)), aligned, (dist, pred)
    return d, list(reversed(equals)), aligned


def diff2html(rows1, rows2, equals, aligned, two_columns=False):
    """
    Produces a HTML report with differences between *rows1*
    and *rows2*.

    :param rows1: first set of rows
    :param rows2: second set of rows
    :param equals: third output of @see fn edit_distance_text
    :param aligned: fourth output of @see fn edit_distance_text
    :param two_columns: displays the differences on two columns
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
    tda = '<td style="background-color:#E59866;"><code style="background-color:#E59866;">'
    tda_ = '</code></td>'
    tdb = '<td style="background-color:#ABEBC6;"><code style="background-color:#ABEBC6;">'
    tdb_ = '</code></td>'
    tdc = '<td style="background-color:#E5E7E9;"><code style="background-color:#E5E7E9;">'
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
            al = char_aligned[a, b]
            if al[0] == 0:
                row.extend([
                    '<td style="background-color:#FFFFFF;">'
                    '<code style="background-color:#FFFFFF;">',
                    str(a), "</code></td>"])
            else:
                row.extend(["<td><code>", str(a), "</code></td>"])

        if b is None:
            row.append("<td></td>")
        elif a is None:
            row.extend([tdb, str(b), tdb_])
        else:
            al = char_aligned[a, b]
            if al[0] == 0:
                row.extend([
                    '<td style="background-color:#FFFFFF;">'
                    '<code style="background-color:#FFFFFF;">',
                    str(b), '</code></td>'])
            else:
                row.extend(["<td><code>", str(b), "</code></td>"])

        if a is None:
            if two_columns:
                row.extend(["<td></td>", tdb, rows2[b], tdb_])
            else:
                row.extend([tdb, rows2[b], tdb_])
        elif b is None:
            if two_columns:
                row.extend([tda, rows1[a], tda_, "<td></td>"])
            else:
                row.extend([tda, rows1[a], tda_])
        else:
            al = char_aligned[a, b]
            if al[0] == 0:
                if two_columns:
                    row.extend([
                        '<td style="background-color:#FFFFFF;">'
                        '<code style="background-color:#FFFFFF;">',
                        rows1[a], '</code></td>',
                        '<td style="background-color:#FFFFFF;">'
                        '<code style="background-color:#FFFFFF;">',
                        rows2[b], '</code></td>'])
                else:
                    row.extend([
                        '<td style="background-color:#FFFFFF;">'
                        '<code style="background-color:#FFFFFF;">',
                        rows1[a], '</code></td>'])
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
                if two_columns:
                    row.extend(
                        [tdc, "".join(l1), "</code>", tdc_,
                         tdc, "<code>", "".join(l2), tdc_])
                else:
                    row.extend(
                        [tdc, "".join(l1), "</code><br /><code>",
                         "".join(l2), tdc_])

        row.append(tr_)
        rows.append("".join(row))
    rows.append("</table>")
    return "\n".join(rows)
