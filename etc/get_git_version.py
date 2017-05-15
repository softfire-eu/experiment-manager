from subprocess import Popen, PIPE


def call_git_describe(abbrev):
    try:
        p = Popen(['git', 'describe', '--tags', '--abbrev=%d' % abbrev],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        line = p.stdout.readlines()[0]
        return line.strip().decode('utf-8')

    except:
        return None


def is_dirty():
    try:
        p = Popen(["git", "diff-index", "--name-only", "HEAD"],
                  stdout=PIPE, stderr=PIPE)
        p.stderr.close()
        lines = p.stdout.readlines()
        return len(lines) > 0
    except:
        return False


def read_release_version():
    try:
        f = open("../RELEASE-VERSION", "r")

        try:
            version = f.readlines()[0]
            return version.strip()

        finally:
            f.close()

    except:
        return None


def increase_version(version):
    f = open("../RELEASE-VERSION", "w")
    ver_int = [int(x) for x in version.split(' ')]
    ver_int[2] = ver_int[2] + 1
    f.write("%s\n" % '.'.join(version))
    f.close()


def get_rev():
    p = Popen(['git', 'log', '--oneline', '-n', '1'], stdout=PIPE, stderr=PIPE)
    p.stderr.close()
    lines = p.stdout.readlines()
    return lines[0].decode('utf-8').split(' ')[0]


def is_release():
    p = Popen(['git', 'log', '-n', '1', '--pretty=%d', 'HEAD'], stdout=PIPE, stderr=PIPE)
    p.stderr.close()
    lines = p.stdout.readlines()
    return "tag" in lines[0].decode('utf-8')


def get_git_version(abbrev=7):
    version = read_release_version()

    if not is_release():
        version += ".b.r" + get_rev()
    else:
        increase_version(version)

    if version is None:
        raise ValueError("Cannot find the version number!")

    return version


if __name__ == "__main__":
    print(get_git_version())
