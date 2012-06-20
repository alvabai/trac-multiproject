If there's something to be fixed in the Trac version we use, you can fix it
and add a patch here.

If the change is not related only to MultiProject use, submit a patch also to the
Trac team so the fix may find its way into the official Trac releases.

====

How to create a patch:
  diff -crB Trac-original Trac-modified-by-you > your.patch

How to apply a patch:
  cd Trac-sources-dir-you-need-to-patch
  patch -p1 < path/to/your.patch

Before applying a patch (and to test your new patch) it is a good idea to
run the patch command with --dry-run parameter to see if there would be any
problems applying the patch.
