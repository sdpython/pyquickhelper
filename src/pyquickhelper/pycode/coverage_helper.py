"""
@file
@brief Publishing coverage
"""
import os
import re
from collections import Counter
import shutil
import pprint
import sqlite3
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO


def _attr_(var, name1, name2):
    try:
        return getattr(var, name1, getattr(var, name2))
    except AttributeError:  # pragma: no cover
        raise AttributeError(
            "Unable to find '{}' or '{}' ({}) in \n{}\n--".format(
                name1, name2, type(var),
                "\n".join(sorted(dir(var)))))


def get_source(cov):
    return cov.config.source


def publish_coverage_on_codecov(path, token, commandline=True, fLOG=None):
    """
    Publishes the coverage report on `codecov <https://codecov.io/>`_.
    See blog post :ref:`blogpost_coverage_codecov`.

    @param      path            path to source
    @param      token           token on codecov
    @param      commandline     see @see cl SourceRepository
    @param      fLOG            logging function
    @return                     out, err from function @see fn run_cmd
    """
    if fLOG is None:
        from ..loghelper import noLOG
        fLOG = noLOG
    # delayed import to speed up import of pycode
    from ..loghelper import SourceRepository
    if os.path.isfile(path) or path.endswith(".xml"):
        report = path
    else:
        report = os.path.join(path, "_doc", "sphinxdoc",
                              "source", "coverage", "coverage_report.xml")

    report = os.path.normpath(report)
    if not os.path.exists(report):
        raise FileNotFoundError(  # pragma: no cover
            "Unable to find '{}'.".format(report))

    proj = os.path.normpath(os.path.join(
        os.path.dirname(report), "..", "..", "..", ".."))

    src = SourceRepository(commandline=commandline)
    last = src.get_last_commit_hash(proj)
    cmd = ["--token={0}".format(token), "--file={0}".format(report),
           "--commit={0}".format(last), "--root={0} -X gcov".format(proj)]
    if token is not None:
        import codecov
        new_out = StringIO()
        new_err = StringIO()
        with redirect_stdout(new_out):
            with redirect_stderr(new_err):
                codecov.main(*cmd)
        out = new_out.getvalue()
        err = new_err.getvalue()
        if err:
            raise RuntimeError(  # pragma: no cover
                "Unable to run:\nCMD:\n{0}\nOUT:\n{1}\n[pyqerror]\n{2}".format(cmd, out, err))
        return out, err
    return cmd


def find_coverage_report(folder, exclude=None, filter_out='.*conda.*'):
    """
    Finds all coverage reports in one subfolder.

    @param      folder      which folder to look at
    @param      exclude     list of subfolder not to look at
    @param      filter_out  filter out from the name
    @return                 list of files ``.coverage``

    The structure is supposed to:

    ::

        folder
          +- hash1
          |    +- date1
          |    |    +- .coverage - not selected
          |    +- date2
          |         +- .coverage - selected
          +- hash2
               +- date
                    +- .coverage - selected
    """
    # delayed import to speed up import of pycode
    from ..filehelper import explore_folder_iterfile
    regexp = re.compile('data_file=([0-9a-zA-Z_]+)')
    regcov = re.compile(
        '<h1>Coveragereport:<spanclass=.?pc_cov.?>([0-9]+)%</span>')
    regout = re.compile(filter_out) if filter_out else None
    covs = {}
    subfold = os.listdir(folder)
    for sub in subfold:
        if exclude is not None and sub in exclude:
            continue
        full = os.path.join(folder, sub)
        keep = []
        nn = None
        cov = None
        for it in explore_folder_iterfile(full):
            name = os.path.split(it)[-1]
            dt = os.stat(full).st_mtime
            if name == 'index.html':
                with open(it, 'r') as f:
                    htd = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
                cont = regcov.findall(htd)
                if len(cont) > 0:
                    cov = cont[0]
            if name == 'covlog.txt':
                with open(it, 'r') as f:
                    logd = f.read()
                cont = regexp.findall(logd)
                if len(cont) > 0:
                    nn = cont[0]
            if name == '.coverage':
                keep.append((dt, it))
        if len(keep) == 0:
            continue
        mx = max(keep)
        if regout is not None and regout.search(nn):
            continue
        covs[sub] = (mx[-1], nn, cov)
    return covs


def coverage_combine(data_files, output_path, source, process=None):
    """
    Merges multiples reports.

    @param      data_files                  report files (``.coverage``)
    @param      output_path                 output path
    @param      source                      source directory
    @param      process                     function which processes the coverage report
    @return                                 coverage report

    The function *process* should have the signature:

    ::

        def process(content):
            # ...
            return content

    On :epkg:`Windows`, file name have to have the right case.
    If not, coverage reports an empty coverage and raises an exception.

    .. versionchanged:: 1.8
        Parameter *remove_unexpected_root* was added.
        The function was refactored to handle better relative files.
    """
    def raise_exc(exc, content, ex, ex2, outfile, destcov, source,
                  dests, inter, cov, infos):  # pragma: no cover

        def shorten(t):
            if len(t) > 2000:
                return t[:2000] + "\n..."
            else:
                return t
        if len(content) > 2000:
            content = content[:2000] + '\n...'
        ex = "\n-\n".join(shorten(_) for _ in ex)
        ex2 = "\n-\n".join(shorten(_) for _ in ex2)
        rows = ['-----------------',
                "destcov='{0}'".format(destcov),
                "outfile='{0}'".format(outfile),
                "source='{0}'".format(source),
                "cov.source={0}".format(get_source(cov)),
                "dests='{0}'".format(';'.join(dests)),
                "inter={0}".format(inter)]
        for ii, info in enumerate(infos):
            rows.append('----------------- {}/{}'.format(ii, len(infos)))
            for k, v in sorted(info.items()):
                rows.append("{}='{}'".format(k, v))
        rows.append('-----------------')
        if cov is not None and _attr_(cov, '_data', 'data')._lines is not None:
            rows.append("##### LINES")
            end = min(5, len(_attr_(cov, '_data', 'data')._lines))
            for k, v in list(sorted(_attr_(cov, '_data', 'data')._lines.items()))[:end]:
                rows.append('   {0}:{1}'.format(k, v))
            rows.append("----- RUNS")
            end = min(5, len(_attr_(cov, '_data', 'data')._runs))
            for k in _attr_(cov, '_data', 'data')._runs[:end]:
                rows.append('   {0}'.format(k))
            rows.append("----- END")

        mes = "{5}. In '{0}'.\n{1}\n{2}\n---AFTER---\n{3}\n---BEGIN---\n{4}"
        raise RuntimeError(mes.format(output_path, "\n".join(
            rows), content, ex, ex2, exc, cov)) from exc

    # We copy the origin coverage if the report is produced
    # in a folder part of the merge.
    destcov = os.path.join(output_path, '.coverage')
    if os.path.exists(destcov):
        destcov2 = destcov + '_old'
        shutil.copy(destcov, destcov2)

    # Starts merging coverage.
    from coverage import Coverage
    cov = Coverage(data_file=destcov, source=[source])
    cov._init()
    cov.get_data()
    if get_source(cov) is None or len(get_source(cov)) == 0:
        raise_exc(FileNotFoundError("Probably unable to find '{0}'".format(source)),
                  "", [], [], "", destcov, source, [], [], cov, [])

    inter = []

    def find_longest_common_root(names, begin):
        counts = {}
        for name in names:
            spl = name.split(begin)
            for i in range(1, len(spl) + 1):
                if spl[i - 1] == 'src':
                    break
                sub = begin.join(spl[:i])
                if sub in counts:
                    counts[sub] += 1
                else:
                    counts[sub] = 1
        item = max((v, k) for k, v in counts.items())
        return item[1]

    def copy_replace(source, dest, root_source, keep_infos):
        shutil.copy(source, dest)

        co = Counter(root_source)
        slash = co.get('/', 0) >= co.get('\\', 0)
        if slash:
            begin = "/"
            root_source_dup = root_source.replace('\\', '/').replace('//', '/')
        else:
            begin = "\\"
            root_source_dup = root_source.replace("\\", "\\\\")

        keep_infos["slash"] = slash
        keep_infos["begin"] = begin
        keep_infos["root_source_dup"] = root_source_dup
        keep_infos["root_source"] = root_source
        keep_infos["source"] = source
        keep_infos["dest"] = dest

        conn = sqlite3.connect(dest)
        sql = []
        names = []
        for row in conn.execute("select * from file"):
            names.append(row[1])
            name = row[1].replace('/', begin)
            if not name.startswith(root_source):
                name = root_source + begin + name
            s = "UPDATE file SET path='{}' WHERE id={};".format(name, row[0])
            sql.append(s)

        keep_infos['root_common'] = find_longest_common_root(names, begin)

        c = conn.cursor()
        for s in sql:
            c.execute(s)
        conn.commit()
        conn.close()

    # We modify the root in every coverage file.
    dests = [os.path.join(output_path, '.coverage{0}'.format(i))
             for i in range(len(data_files))]
    infos = []
    for fi, de in zip(data_files, dests):
        keep_infos = {}
        copy_replace(fi, de, source, keep_infos)
        infos.append(keep_infos)
        shutil.copy(de, de + "~")

    # Keeping information (for exception).
    ex = []
    for d in dests:
        with open(d, "rb") as f:
            ex.append(f.read())
    ex2 = []
    for d in data_files:
        with open(d, "rb") as f:
            ex2.append(f.read())

    # We replace destcov by destcov2 if found in dests.
    if destcov in dests:
        ind = dests.index(destcov)
        dests[ind] = destcov2

    # Let's combine.
    cov.combine(dests)  # dest
    cov.save()
    report = True

    from coverage.misc import NoSource, CoverageException
    try:
        cov.html_report(directory=output_path,
                        ignore_errors=True)
    except NoSource as e:
        raise_exc(e, "", ex, ex2, "", destcov, source,
                  dests, inter, cov, infos)
    except CoverageException as e:
        if "No data to report" in str(e):
            # issue with path
            report = False
        else:
            msg = pprint.pformat(infos)
            raise RuntimeError(  # pragma: no cover
                "Unable to process report in '{0}'.\n----\n{1}".format(
                    output_path, msg)) from e

    if report:
        outfile = os.path.join(output_path, "coverage_report.xml")
        cov.xml_report(outfile=outfile)
        cov.save()

        # Verifications
        with open(outfile, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) == 0:
            raise RuntimeError("No report was generated.")

    return cov
