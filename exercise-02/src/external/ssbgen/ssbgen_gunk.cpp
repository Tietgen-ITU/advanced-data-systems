#include "include/ssbgen_gunk.hpp"

#include "include/dsstypes.h"
#include "include/dss.h"
#include "bm_utils.cpp"

void load_distributions()
{
    read_dist("p_cntr", &p_cntr_set);
    read_dist("colors", &colors);
    read_dist("p_types", &p_types_set);
    read_dist("nations", &nations);
    read_dist("regions", &regions);
    read_dist("o_oprio", &o_priority_set);
    read_dist("instruct", &l_instruct_set);
    read_dist("smode", &l_smode_set);
    read_dist("category", &l_category_set);
    read_dist("rflag", &l_rflag_set);
    read_dist("msegmnt", &c_mseg_set);

    /* load the distributions that contain text generation */
    read_dist("nouns", &nouns);
    read_dist("verbs", &verbs);
    read_dist("adjectives", &adjectives);
    read_dist("adverbs", &adverbs);
    read_dist("auxillaries", &auxillaries);
    read_dist("terminators", &terminators);
    read_dist("articles", &articles);
    read_dist("prepositions", &prepositions);
    read_dist("grammar", &grammar);
    read_dist("np", &np);
    read_dist("vp", &vp);

    // init_exit_pool() --> in the dbgen_gunk.cpp file from tpch extension
}

static void cleanup_distribution(distribution *target)
{
    if (!target)
        return;

    if (target->list)
    {
        for (int i = 0; i < target->count; i++)
        {
            if (target->list[i].text)
                free(target->list[i].text);
        }
    }
}

void cleanup_distributions()
{
    cleanup_distribution(&p_cntr_set);
    cleanup_distribution(&colors);
    cleanup_distribution(&p_types_set);
    cleanup_distribution(&nations);
    cleanup_distribution(&regions);
    cleanup_distribution(&o_priority_set);
    cleanup_distribution(&l_instruct_set);
    cleanup_distribution(&l_smode_set);
    cleanup_distribution(&l_category_set);
    cleanup_distribution(&l_rflag_set);
    cleanup_distribution(&c_mseg_set);
    cleanup_distribution(&nouns);
    cleanup_distribution(&verbs);
    cleanup_distribution(&adjectives);
    cleanup_distribution(&adverbs);
    cleanup_distribution(&auxillaries);
    cleanup_distribution(&terminators);
    cleanup_distribution(&articles);
    cleanup_distribution(&prepositions);
    cleanup_distribution(&grammar);
    cleanup_distribution(&np);
    cleanup_distribution(&vp);
}
