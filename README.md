[![codecov](https://codecov.io/gh/clubby789/LaserPy/branch/master/graph/badge.svg?token=X758BLBSAU)](undefined)

# LaserPy
A Python implementation of [LaserLang](https://github.com/Quintec/LaserLang).
I'll leave the full documentation there, and only note down here currently implemented instructions, or implementation-specific changes.

## Currently Implemented
### Mirrors
`\ / v ^ < > ⌞ ⌜ ⌟ ⌝`
### Strings
`"` (String Mode)

``` ` ``` (Raw Mode)
### Unary Operations
`( ) c r R ! ~ p P o O b n B`
### Binary Operations
`+ - × ÷ * g l = & | %`

## Implementation Notes
Any numeric strings pushed into memory will be automatically cast to integers

