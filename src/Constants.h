#ifndef COVIDSIM_CONSTANTS_H_INCLUDED_
#define COVIDSIM_CONSTANTS_H_INCLUDED_

#include "Country.h"

/**
 * Math constant defined as the ratio of a circle's circumference to its diameter.
 *
 * TODO: since all calculations using this constant are being automatically
 * type-casted to double, should the precision be extended for more accuracy in
 * the simulations?
 *
 * Eventually could be replaced with C++20's std::numbers::pi.
 * https://en.cppreference.com/w/cpp/header/numbers
 */
constexpr double PI = 3.1415926535; // full double precision: 3.14159265358979323846

/**
 * An arc minute of latitude along any line of longitude in meters.
 *
 * Also known as the International Nautical Mile.
 *
 * @see https://en.wikipedia.org/wiki/Nautical_mile
 */
constexpr int NMI = 1852;

/**
 * The number of arc minutes in one degree.
 *
 * @see https://en.wikipedia.org/wiki/Minute_and_second_of_arc
 */
constexpr int ARCMINUTES_PER_DEGREE = 60;

/**
 * The number of degrees in a complete rotation.
 *
 * @see https://en.wikipedia.org/wiki/Turn_(angle)
 */
constexpr int DEGREES_PER_TURN = 360;

/**
 * The earth's circumference in meters.
 *
 * The units of cancellation:
 *    meters/minute * minutes/degree * degrees = meters
 */
constexpr int EARTH_CIRCUMFERENCE = NMI * ARCMINUTES_PER_DEGREE * DEGREES_PER_TURN;

/**
 * The earth's diameter in meters.
 */
constexpr double EARTH_DIAMETER = EARTH_CIRCUMFERENCE / PI;

/**
 * The Earth's radius in meters.
 *
 * The previous hardcoded value used 6366707 which was derived from the
 * following formula:
 *
 *     Earth's radius (m) = Earth's circumference / 2 * Pi
 *
 * where Earth's circumference can be derived with the following formula:
 *
 *     Earth's circumference (m) = NMI * ARCMINUTES_PER_DEGREE * DEGREES_PER_TURN
 */
constexpr double EARTHRADIUS = EARTH_DIAMETER / 2;

const int OUTPUT_DIST_SCALE = 1000;
const int MAX_PLACE_SIZE = 20000;
const int MAX_NUM_SEED_LOCATIONS = 10000;

const int MAX_CLP_COPIES = 50;

const int CDF_RES = 20; // resolution of (inverse) cumulative distribution functions, used mostly for severity progressions/delay distributions.
const int INFPROF_RES = 56;

const int NUM_AGE_GROUPS = 17;
const int AGE_GROUP_WIDTH = 5;
const int DAYS_PER_YEAR = 364;
const int INFECT_TYPE_MASK = 16;
const int MAX_GEN_REC = 20;
const int MAX_SEC_REC = 500;
const int INF_QUEUE_SCALE = 5;
const int MAX_TRAVEL_TIME = 14;

const int MAX_INFECTIOUS_STEPS = 2550;

const int MAX_NUM_THREADS = 96;
const int CACHE_LINE_SIZE = 64;

// define maximum number of contacts
const int MAX_CONTACTS = 500;

const int MAX_DUR_IMPORT_PROFILE = 10245;

const int MAX_AIRPORTS = 5000;
const int NNA = 10;
// Need to use define for MAX_DIST_AIRPORT_TO_HOTEL to avoid differences between GCC and clang in requirements to share const doubles in OpenMP default(none) pragmas
#define MAX_DIST_AIRPORT_TO_HOTEL 200000.0
const int MIN_HOTELS_PER_AIRPORT = 20;
const int HOTELS_PER_1000PASSENGER = 10;


const int MAX_NUM_INTERVENTION_CHANGE_TIMES = 100; /**< For various "over time" parameters that allow scaling of NPI effectiveness. */
const int MAX_NUM_CFR_CHANGE_TIMES = 100; /**< To allow IFR to scale over time. */

// MS generates a lot of C26451 overflow warnings. Below is shorthand
// to increase the cast size and clean them up.

#define _I64(x) static_cast<int64_t>(x)

// Settings (numbers not arbitrary - don't change without checking)
// const int PrimarySchool		= 0; 
// const int SecondarySchool	= 1; 
// const int University		= 2; 
// const int Workplace			= 3; 
const int House				= MAX_NUM_PLACE_TYPES;      // Max number of potential place types.
const int Spatial			= MAX_NUM_PLACE_TYPES + 1;  // community

// NPIs
const int CaseIsolation				= 0;
const int HomeQuarantine			= 1;
const int PlaceClosure				= 2;
const int SocialDistancing			= 3; 
const int EnhancedSocialDistancing	= 4; 
const int DigContactTracing			= 5; 


#endif // COVIDSIM_CONSTANTS_H_INCLUDED_
