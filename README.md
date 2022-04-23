# cutme

C Unit Testing Made Easy. Because writing C is hard enough.

## Pronunciacion

Coo-Taa-May

## Theory of Operation

Provide an object file compiled with these gcc flags: `-g3 -gdwarf-4`.
cutme will determine which mocks need to be created based on information in the debug info.
cutme will then compile an application and run your tests.

