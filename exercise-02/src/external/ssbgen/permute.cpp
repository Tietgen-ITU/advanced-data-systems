/* @(#)permute.c	2.1.8.3 */
/*
 * permute.c -- a permutation generator for the query
 *              sequences in TPC-H and TPC-R
 */

#include "include/config.h"
#include "include/dss.h"

long NextRand(long seed);
long *permute(long *set, int cnt, long stream);
long *permute_dist(distribution *d, long stream);
long seed;
char *eol[2] = {" ", "},"};
extern seed_t Seed[];

#define MAX_QUERY 22
#define ITERATIONS 1000
#define UNSET 0

long *permute(long *a, int c, long s)
{
	int i;
	static long source;
	static long *set, temp;

	if (a != (long *)NULL)
	{
		set = a;
		for (i = 0; i < c; i++)
			*(a + i) = i;
		for (i = 0; i < c; i++)
		{
			RANDOM(source, 0L, (long)(c - 1), s);
			temp = *(a + source);
			*(a + source) = *(a + i);
			*(a + i) = temp;
			source = 0;
		}
	}
	else
		source += 1;

	if (source >= c)
		source -= c;

	return (set + source);
}

long *permute_dist(distribution *d, long stream)
{
	static distribution *dist = NULL;
	int i;

	if (d != NULL)
	{
		if (d->permute == (long *)NULL)
		{
			d->permute = (long *)malloc(sizeof(long) * DIST_SIZE(d));
			MALLOC_CHECK(d->permute);
			for (i = 0; i < DIST_SIZE(d); i++)
				*(d->permute + i) = i;
		}
		dist = d;
		return (permute(dist->permute, DIST_SIZE(dist), stream));
	}

	if (dist != NULL)
		return (permute(NULL, DIST_SIZE(dist), stream));
	else
		INTERNAL_ERROR("Bad call to permute_dist");
}
