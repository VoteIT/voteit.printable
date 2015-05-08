 #!/bin/bash
 #You need lingua and gettext installed to run this
 
 echo "Updating voteit.printable.pot"
 pot-create -d voteit.printable -o voteit/printable/locale/voteit.printable.pot .
 echo "Merging Swedish localisation"
 msgmerge --update voteit/printable/locale/sv/LC_MESSAGES/voteit.printable.po voteit/printable/locale/voteit.printable.pot
 echo "Updated locale files"
 