from random import sample, random

# CONSTANT
POPULATION = 100
GENES = 6
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

def genetic_algorithm_recommender(restaurants, users):
    
    # return: number
    def compute_fitness(chromosome_value):
        group_score = 0

        for user in users:
            score_sum = 0
            user_categories = user['categories']
            user_categories_set = set(user_categories)
            user_price_range = user.get('price_range', -1) 
            if not user_price_range:
                user_price_range = -1

            for index in chromosome_value:
                score = 0
                restaurant = restaurants[index]
                restaurant_categories = [category['name_en'] for category in restaurant['profile']['categories']]
                restaurant_price_range = restaurant['profile'].get('price_range', -1)
                if not restaurant_price_range:
                    restaurant_price_range = -1
                
                preference_score = 0
                for index, user_category in enumerate(user_categories):
                    if user_category in restaurant_categories:
                        preference_score += len(user_categories) - index
                price_score = 1 if restaurant_price_range > -1 and restaurant_price_range <= user_price_range else 0
                
                score = preference_score + price_score
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
        return [sample(range(len(restaurants)), GENES) for _ in range(POPULATION)]


    def is_converged(generation_highest_fitnesses):
        return len(generation_highest_fitnesses) > CONVERGED_NUMBER and generation_highest_fitnesses[-1] == generation_highest_fitnesses[-CONVERGED_NUMBER]


    population = initialize_population()
    generation_highest_fitnesses = []

    number_of_generation = 0
    while True:
        number_of_generation += 1
        chromosomes = add_fitness_for_population(population)
        highest_fitness_chromosome = max(chromosomes)
        generation_highest_fitnesses.append(highest_fitness_chromosome[0])
        # print(f"Gen#{number_of_generation}: {highest_fitness_chromosome}")
        if number_of_generation == 100 or is_converged(generation_highest_fitnesses):
            print(highest_fitness_chromosome)
            print(generation_highest_fitnesses)
            return [restaurants[index] for index in highest_fitness_chromosome[1]]
        pairs = get_pairs(chromosomes)
        population = generate_new_generation(pairs)


def test_genetic_algorithm_recommender():
    import requests
    from pprint import pprint
    response = requests.get('https://neutron-dot-restaurant-recommender-system.et.r.appspot.com/api/restaurants/nearby?lat=13.64999266005064&lon=100.49433963566172&dist=10000&limit=100')
    input_restaurants = response.json()[:50]
    user_irin = {
        "name": "irin",
        "categories": ['Korean Restaurant', 'Japanese Restaurant', 'Italian Restaurant', 'Thai Restaurant', 'Shabu Shabu Restaurant'],
        "price_range": 2,
    }
    user_north = {
        "name": "north",
        "categories": ['Thai Restaurant', 'Japanese Restaurant', 'Korean Restaurant', 'Shabu Shabu Restaurant', 'Steakhouse'],
        "price_range": 3,
    }
    users = [user_irin, user_north]
    recommended_retaurants = genetic_algorithm_recommender(input_restaurants, users)
    pprint([restaurant['name'] for restaurant in recommended_retaurants])


if __name__ == '__main__':
    test_genetic_algorithm_recommender()
    