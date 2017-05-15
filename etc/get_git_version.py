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


def read_release_version(file):
    try:
        f = open(file, "r")

        try:
            version = f.readlines()[0]
            return version.strip()

        finally:
            f.close()
    except:
        return None


def increase_version(version, file):
    f = open(file, "w")
    ver_int = [int(x) for x in version.split('.')]
    ver_int[2] = ver_int[2] + 1
    ver_str = [str(x) for x in ver_int]
    f.write("%sb0\n" % '.'.join(ver_str))
    f.close()


def is_release(version):
    return "b" not in version


def get_version(file='RELEASE-VERSION'):
    version = read_release_version(file)

    if version is None:
        raise ValueError("Cannot find the version number!")

    if is_release(version):
        increase_version(version, file)

    return version


if __name__ == "__main__":
    print(get_version('../RELEASE-VERSION'))
