# Packaging for Windows #

I spent some time trying to package pyconquer as a Windows executable.

First problem is the code in pyconquer.py:
pygame.display.set\_icon(pygame.image.load(graphics\_path+"soldier.png"))

After problems with py2exe I went with Pygame PAckage Builder http://www.moviepartners.com/blog/utilities/ppb/
but problems persisted (path related problem, or due to not packaging the icon resource with executable).

Uncommenting the above line got me further, but now conquer.exe raises an error when run:
Microsoft Visual C++ Runtime Library: Runtime Error.
I guess it's possible the runtime library would have to be included, if that was the case it seems it's not quite trivial from the legal point of view.