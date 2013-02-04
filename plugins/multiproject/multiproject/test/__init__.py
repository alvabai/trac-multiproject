import sys, os

# add parent dir to sys.path
sys.path.append(
    os.path.normpath(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "."
        )
    )
)

print "\n".join(sys.path)

