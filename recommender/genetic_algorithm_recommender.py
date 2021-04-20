from random import sample, random

# CONSTANT
POPULATION = 100
PAIRS = int(POPULATION / 2)
TOP_N = 30
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.5
CONVERGED_NUMBER = 15

# Types
# Chromosome: (number (fitness), ChromosomeValue)
# ChromosomeValue: number[number (index)]
# Restaurant: {
#     _id: string
#     profile: {
#         categories: {
#             name_en: string
#         }[]
#         price_range: number
#     }
# }
# User: {
#     categories: string[]
#     price_range: number
# }

def genetic_algorithm_recommender(restaurants, users, genes=6, get_matrix=False, varbose=False):
    
    # return: number
    def compute_fitness(chromosome_value):
        group_score = 0

        for user in users:
            score_sum = 0
            user_categories = user['categories']
            user_categories_set = set(user_categories)
            user_price_range = user.get('price_range', -1) 
            if not user_price_range:
                user_price_range = None

            for index in chromosome_value:
                score = 0
                restaurant = restaurants[index]
                restaurant_categories = [category['name_en'] for category in restaurant['profile']['categories']]
                restaurant_price_range = restaurant['profile']['price_range'] or None
                restaurant_distance = restaurant['dist']['calculated'] or None
                
                preference_score = 0
                for index, user_category in enumerate(user_categories):
                    if user_category in restaurant_categories:
                        preference_score += len(user_categories) - index

                price_score = 0
                if user_price_range and restaurant_price_range:
                    gap = user_price_range - restaurant_price_range
                    if gap == 0:
                        price_score = 3
                    elif gap == 1:
                        price_score = 2
                    elif gap == 2:
                        price_score = 1

                distance_score = 0
                if restaurant_distance:
                    if restaurant_distance < 1000:
                        distance_score = 3
                    elif restaurant_distance < 3000:
                        distance_score = 1

                history_score = 0
                
                score = preference_score + price_score + distance_score + history_score
                score_sum += score

            group_score += score_sum
            
        return group_score


    def get_top_n_chromosomes(chromosomes, top_n):
        return sorted(chromosomes, key= lambda chromosome: chromosome[0], reverse=True)[:top_n]


    # return: [(list[] (ChromosomeValue), list (ChromosomeValue))]
    def get_pairs(chromosomes):
        pairs = []
        selected_chromosomes = get_top_n_chromosomes(chromosomes, TOP_N)
        for _ in range(PAIRS):
            new_pair = []
            count = 0
            while True:
                if count == 100:
                    break
                new_pair = sample(range(len(selected_chromosomes)), 2)
                count += 1
                if new_pair not in pairs:
                    pairs.append(new_pair)
                    break
        return [(selected_chromosomes[pair[0]], selected_chromosomes[pair[1]]) for pair in pairs]


    # return [ChromosomeValue, ChromosomeValue]
    def crossover(chromosome_value_1, chromosome_value_2):
        new_chromosome_value_1 = []
        new_chromosome_value_2 = []
        for index, each_chromosome_value_1 in enumerate(chromosome_value_1):
            each_new_chromosome_value_1 = chromosome_value_1[index]
            each_new_chromosome_value_2 = chromosome_value_2[index]
            
            is_swap = False
            if each_chromosome_value_1 not in chromosome_value_2 and each_new_chromosome_value_2 not in chromosome_value_1 and random() < CROSSOVER_RATE:
                is_swap = True
            
            if is_swap:
                each_new_chromosome_value_1 = chromosome_value_2[index]
                each_new_chromosome_value_2 = chromosome_value_1[index]
                
            new_chromosome_value_1.append(each_new_chromosome_value_1)
            new_chromosome_value_2.append(each_new_chromosome_value_2)
        return [new_chromosome_value_1, new_chromosome_value_2]


    def mutate(chromosome_value):
        if random() < MUTATION_RATE:
            mutated_chromosome_value = []
            for each_chromosome_value in chromosome_value:
                if random() < MUTATION_RATE:
                    count = 0
                    while True:
                        if count == 100:
                            mutated_chromosome_value.append(each_chromosome_value)
                            break
                        else:
                            count += 1
                            new_gene = sample(range(len(restaurants)), 1)[0]
                            if new_gene not in chromosome_value and new_gene not in mutated_chromosome_value:
                                mutated_chromosome_value.append(new_gene)
                                break
                else:
                    mutated_chromosome_value.append(each_chromosome_value)
            return [chromosome_value, mutated_chromosome_value]
                
        return [chromosome_value]


    def generate_new_generation(pairs):
        crossovered_chromosomes = []
        new_generation = []
        # crossover
        for pair in pairs:
            chromosome_1 = pair[0]
            chromosome_2 = pair[1]
            new_chromosomes = crossover(chromosome_1[1], chromosome_2[1])
            crossovered_chromosomes += new_chromosomes
        # mutation
        for chromosome_value in crossovered_chromosomes:
            new_generation += mutate(chromosome_value)
        return new_generation


    def add_fitness_for_population(chromosome_values):
        return [(compute_fitness(chromosome_value), chromosome_value) for chromosome_value in chromosome_values]


    def initialize_population():
        # check for dup
        return [sample(range(len(restaurants)), genes) for _ in range(POPULATION)]


    def is_converged(generation_highest_fitnesses):
        return len(generation_highest_fitnesses) > CONVERGED_NUMBER and generation_highest_fitnesses[-1] == generation_highest_fitnesses[-CONVERGED_NUMBER]


    population = initialize_population()
    generation_highest_fitnesses = []
    generation_highest_fitness_chromosomes = []

    number_of_generation = 0
    while True:
        number_of_generation += 1
        chromosomes = add_fitness_for_population(population)
        highest_fitness_chromosome = max(chromosomes)
        generation_highest_fitnesses.append(highest_fitness_chromosome[0])
        generation_highest_fitness_chromosomes.append(highest_fitness_chromosome)
        print(f"Gen#{number_of_generation}: {highest_fitness_chromosome}") if varbose else ''
        if number_of_generation == 100 or is_converged(generation_highest_fitnesses):
            print(f"Result: {highest_fitness_chromosome}") if varbose else ''
            recommended_restaurants = [restaurants[index] for index in highest_fitness_chromosome[1]]
            return recommended_restaurants if not get_matrix else (recommended_restaurants, generation_highest_fitness_chromosomes)
        pairs = get_pairs(chromosomes)
        population = generate_new_generation(pairs)


def test_genetic_algorithm_recommender(count=6):
    # import requests
    
    import json
    # response = requests.get('https://neutron-dot-restaurant-recommender-system.et.r.appspot.com/api/restaurants/nearby?lat=13.64999266005064&lon=100.49433963566172&dist=10000&limit=100')
    with open('recommender/test_data/nearby_restaurants.json') as f:
        response = json.load(f)
    input_restaurants = response
    input_restaurants = [restaurant for restaurant in input_restaurants if restaurant['type'] == 'restaurant']
    user_irin = {
        "name": "irin",
        "categories": ['Korean', 'Japanese', 'Italian', 'Thai', 'Shabu Shabu'],
        "price_range": 2,
    }
    user_north = {
        "name": "north",
        "categories": ['Thai', 'Japanese', 'Korean', 'Shabu Shabu', 'Steakhouse'],
        "price_range": 3,
    }
    users = [user_irin, user_north]
    recommended_retaurants, generations = genetic_algorithm_recommender(input_restaurants, users, get_matrix=True, genes=count)
    # pprint([(restaurant['name'], [cat['name_en'] for cat in restaurant['profile']['categories']]) for restaurant in recommended_retaurants])
    return recommended_retaurants, generations


if __name__ == '__main__':
    from pprint import pprint
    recommended_retaurants, generations = test_genetic_algorithm_recommender(count=6)
    pprint(generations)
    pprint([(restaurant['name'], [cat['name_en'] for cat in restaurant['profile']['categories']], restaurant['profile']['price_range']) for restaurant in recommended_retaurants])
    