import time
import argparse
try:
    from psp import Pv
except ImportError:
    Pv = None

template = """#include "pds/config/EventcodeTiming.hh"

#include <stdint.h>

struct slot_s { 
  unsigned code;
  unsigned tick;
};

typedef struct slot_s slot_t;

static const unsigned EvrClkRate = 119000000;

/*
**
**  Timing at %s
**    These values were taken from EVNT:SYS0:1:DELAY
**    Our evrsnoop reports values 50 ticks less, likely
**    because eventcode 0x7d (the fiducial sequence end) is at tick 50
**
**  This structure will be filled by EVNT:SYS0:1:DELAY at runtime.
*/

static slot_t slots[] = { 
  {   0, %5d },
  {   1, %5d },
  {   2, %5d },
  {   3, %5d },
  {   4, %5d },
  {   5, %5d },
  {   6, %5d },
  {   7, %5d },
  {   8, %5d },
  {   9, %5d },

  {  10, %5d },
  {  11, %5d },
  {  12, %5d },
  {  13, %5d },
  {  14, %5d },
  {  15, %5d },
  {  16, %5d },
  {  17, %5d },
  {  18, %5d },
  {  19, %5d },

  {  20, %5d },
  {  21, %5d },
  {  22, %5d },
  {  23, %5d },
  {  24, %5d },
  {  25, %5d },
  {  26, %5d },
  {  27, %5d },
  {  28, %5d },
  {  29, %5d },

  {  30, %5d },
  {  31, %5d },
  {  32, %5d },
  {  33, %5d },
  {  34, %5d },
  {  35, %5d },
  {  36, %5d },
  {  37, %5d },
  {  38, %5d },
  {  39, %5d },

  {  40, %5d },
  {  41, %5d },
  {  42, %5d },
  {  43, %5d },
  {  44, %5d },
  {  45, %5d },
  {  46, %5d },
  {  47, %5d },
  {  48, %5d },
  {  49, %5d },

  {  50, %5d },
  {  51, %5d },
  {  52, %5d },
  {  53, %5d },
  {  54, %5d },
  {  55, %5d },
  {  56, %5d },
  {  57, %5d },
  {  58, %5d },
  {  59, %5d },

  {  60, %5d },
  {  61, %5d },
  {  62, %5d },
  {  63, %5d },
  {  64, %5d },
  {  65, %5d },
  {  66, %5d },
  {  67, %5d },
  {  68, %5d },
  {  69, %5d },

  {  70, %5d },
  {  71, %5d },
  {  72, %5d },
  {  73, %5d },
  {  74, %5d },
  {  75, %5d },
  {  76, %5d },
  {  77, %5d },
  {  78, %5d },
  {  79, %5d },

  {  80, %5d },
  {  81, %5d },
  {  82, %5d },
  {  83, %5d },
  {  84, %5d },
  {  85, %5d },
  {  86, %5d },
  {  87, %5d },
  {  88, %5d },
  {  89, %5d },

  {  90, %5d },
  {  91, %5d },
  {  92, %5d },
  {  93, %5d },
  {  94, %5d },
  {  95, %5d },
  {  96, %5d },
  {  97, %5d },
  {  98, %5d },
  {  99, %5d },

  { 100, %5d },
  { 101, %5d },
  { 102, %5d },
  { 103, %5d },
  { 104, %5d },
  { 105, %5d },
  { 106, %5d },
  { 107, %5d },
  { 108, %5d },
  { 109, %5d },

  { 110, %5d },
  { 111, %5d },
  { 112, %5d },
  { 113, %5d },
  { 114, %5d },
  { 115, %5d },
  { 116, %5d },
  { 117, %5d },
  { 118, %5d },
  { 119, %5d },

  { 120, %5d },
  { 121, %5d },
  { 122, %5d },
  { 123, %5d },
  { 124, %5d },
  { 125, %5d },
  { 126, %5d },
  { 127, %5d },
  { 128, %5d },
  { 129, %5d },

  { 130, %5d },
  { 131, %5d },
  { 132, %5d },
  { 133, %5d },
  { 134, %5d },
  { 135, %5d },
  { 136, %5d },
  { 137, %5d },
  { 138, %5d },
  { 139, %5d },

  { 140, %5d },
  { 141, %5d },
  { 142, %5d },
  { 143, %5d },
  { 144, %5d },
  { 145, %5d },
  { 146, %5d },
  { 147, %5d },
  { 148, %5d },
  { 149, %5d },

  { 150, %5d },
  { 151, %5d },
  { 152, %5d },
  { 153, %5d },
  { 154, %5d },
  { 155, %5d },
  { 156, %5d },
  { 157, %5d },
  { 158, %5d },
  { 159, %5d },

  { 160, %5d },
  { 161, %5d },
  { 162, %5d },
  { 163, %5d },
  { 164, %5d },
  { 165, %5d },
  { 166, %5d },
  { 167, %5d },
  { 168, %5d },
  { 169, %5d },

  { 170, %5d },
  { 171, %5d },
  { 172, %5d },
  { 173, %5d },
  { 174, %5d },
  { 175, %5d },
  { 176, %5d },
  { 177, %5d },
  { 178, %5d },
  { 179, %5d },

  { 180, %5d },
  { 181, %5d },
  { 182, %5d },
  { 183, %5d },
  { 184, %5d },
  { 185, %5d },
  { 186, %5d },
  { 187, %5d },
  { 188, %5d },
  { 189, %5d },

  { 190, %5d },
  { 191, %5d },
  { 192, %5d },
  { 193, %5d },
  { 194, %5d },
  { 195, %5d },
  { 196, %5d },
  { 197, %5d },
  { 198, %5d },
  { 199, %5d },

  { 200, %5d },
  { 201, %5d },
  { 202, %5d },
  { 203, %5d },
  { 204, %5d },
  { 205, %5d },
  { 206, %5d },
  { 207, %5d },
  { 208, %5d },
  { 209, %5d },

  { 210, %5d },
  { 211, %5d },
  { 212, %5d },
  { 213, %5d },
  { 214, %5d },
  { 215, %5d },
  { 216, %5d },
  { 217, %5d },
  { 218, %5d },
  { 219, %5d },

  { 220, %5d },
  { 221, %5d },
  { 222, %5d },
  { 223, %5d },
  { 224, %5d },
  { 225, %5d },
  { 226, %5d },
  { 227, %5d },
  { 228, %5d },
  { 229, %5d },

  { 230, %5d },
  { 231, %5d },
  { 232, %5d },
  { 233, %5d },
  { 234, %5d },
  { 235, %5d },
  { 236, %5d },
  { 237, %5d },
  { 238, %5d },
  { 239, %5d },

  { 240, %5d },
  { 241, %5d },
  { 242, %5d },
  { 243, %5d },
  { 244, %5d },
  { 245, %5d },
  { 246, %5d },
  { 247, %5d },
  { 248, %5d },
  { 249, %5d },

  { 250, %5d },
  { 251, %5d },
  { 252, %5d },
  { 253, %5d },
  { 254, %5d },
  { 255, %5d },
};
                                 

void Pds_ConfigDb::EventcodeTiming::timeslot(unsigned* ticks)
{
  for(unsigned i=0; i<256; i++)
    slots[i].tick = ticks[i];
}

unsigned Pds_ConfigDb::EventcodeTiming::timeslot(unsigned code)
{
  return slots[code].tick;
}

unsigned Pds_ConfigDb::EventcodeTiming::period(unsigned code)
{
  switch(code) {
  case 40:
  case 140: return EvrClkRate/120;
  case 41:
  case 141: return EvrClkRate/ 60;
  case 42:
  case 142: return EvrClkRate/ 30;
  case 43:
  case 143: return EvrClkRate/ 10;
  case 44:
  case 144: return EvrClkRate/  5;
  case 45:
  case 145: return EvrClkRate;
  case 46:
  case 146: return EvrClkRate*  2;
  default:  return unsigned(-1);
  }
}
"""

def generate_file(outname, pvname):
    # get the delay data from the pv
    delay =  Pv.get(pvname)

    with open(outname, "w") as outfile:
        outfile.write(template % ((time.strftime("%b %d, %Y"),) + delay))

if __name__ == "__main__":
    if Pv is None:
        print("psp module is required for this script!")
        sys.exit(1)
    else:
        parser = argparse.ArgumentParser(description='Generate eventcode delay structrure')

        parser.add_argument("-f", "--filename", default="EventcodeTiming.cc",
                            help="the name of the output file")
        parser.add_argument("-d", "--delay", default="EVNT:SYS0:1:DELAY",
                            help="the pv containing the eventcode delays")         
        args = parser.parse_args()

        generate_file(args.filename, args.delay)
