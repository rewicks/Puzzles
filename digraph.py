import argparse, random, json, time

# simple function to allow me to copy and paste the words from the internet but transpose them into
# an easier format
def format_raw(size):
	words_format = open("words-" + str(size) + ".txt", 'w')
	with open("words-raw-" + str(size) + ".txt", 'r') as raw:
		for line in raw:
			words = line.split()
			for w in words:
				words_format.write(w.upper() + "\n")


# adds the words to a dictionary so the storage is quick, efficient, and minimal
# similar in structure to a hash of hashes
def add_to_dictionary(prefix, ending, digraph_size, dictionary):
	if len(ending) == digraph_size:
		if prefix not in dictionary:
			dictionary[prefix] = []
		dictionary[prefix].append(ending)
	else:
		if prefix not in dictionary:
			dictionary[prefix] = {}
		add_to_dictionary(ending[:digraph_size], ending[digraph_size:], digraph_size, dictionary[prefix])

# returns if the given word is in our pre-created dictionary
def find_word(dictionary, word, digraph_size):
	if len(word) == digraph_size:
		if word in dictionary:
			return True
		else:
			return False
	if word[:digraph_size] in dictionary:
		return find_word(dictionary[word[:digraph_size]], word[digraph_size:], digraph_size)
	return False

# reads in a file -- generic so as to allow for different flavors of the game such as longer words
# or n-graphs larger than 2. Please ignore how the code will consider all of these digraphs though
def read_in(word_size, digraph_size):
	dictionary = {}
	with open("words-" + str(word_size) + ".txt", 'r') as inputFile:
		for word in inputFile:
			word = word.strip()
			add_to_dictionary(word[:digraph_size], word[digraph_size:], digraph_size, dictionary)
	return dictionary

# permutates a list to a given size of 'choose' ie 5 choose 3
def permutate(digraphs, choose):
	if len(digraphs) == len(digraphs)-choose:
		return [[]]
	permutations = []
	for d in range(len(digraphs)):
		di = [digraphs[d]]

		leftovers = digraphs[:d] + digraphs[d+1:]
		leftovers_permutations = permutate(leftovers, choose-1)
		for l in leftovers_permutations:			
			permutations.append(di + l)
	return permutations

# given a list of digraphs, it returns the strings of all the words
# each of these wrods must be valid in order to be a valid solution
def get_words(guess, digraph_size, word_size):
	length = word_size / digraph_size
	words = []
	for x in range(len(guess)):
		word_list = []
		for y in range(length):
			word_list.append( guess[ (x+y) % len(guess) ] )
		words.append(''.join(word_list))
	return words

# checks the solution to make sure that all of the words are in our dictionary
def is_valid(guess, dictionary, digraph_size, word_size):
	total_words = get_words(guess, digraph_size, word_size)
	for t in total_words:
		if not find_word(dictionary, t, digraph_size):
			return False
	return True

# generates all possible n-graphs given the size parameter
# could eventually have some heuristics about illegal english consonant clusters, etc
def generate_digraphs(digraph_size):
	if digraph_size == 0:
		return ['']
	digraphs = []
	for letter in range(65,91):
		suffixes = generate_digraphs(digraph_size-1)
		for s in suffixes:
			digraphs.append(chr(letter) + s)
	return digraphs

# returns if the guess is a solution and also if it is unique
def unique_solution(guess, digraph_size, word_size, dictionary):
	alternate_answers = permutate(guess, len(guess))
	correct = 0
	correct_answers = []

	# if not is_valid(guess, dictionary, digraph_size, word_size):
	# 	#print('incorrect solution')
	# 	return False

	for each in alternate_answers:
		if is_valid(each, dictionary, digraph_size, word_size):
			correct += 1
			correct_answers.append(each)
	if correct !=len(guess):
		#print('correct solutions: ' + str(correct/len(guess)))
		return False
	else:
		return True

# gives all subsets of size 'size' of the superset 'superset'
def get_subsets(superset, size):
	if size == 0:
		return [[]]
	subsets = []
	for i in range(len(superset)):
		item = superset[i]

		leftovers = superset[i+1:]
		leftovers_subsets = get_subsets(leftovers, size-1)
		for l in leftovers_subsets:
			subsets.append([item] + l)
	return subsets

# an heuristic function that significantly cuts down on the runtime
# it will not permutate a game to check for multiple solutions if there is
# a digraph in the game that does not pair with any other digraphs
# this may slow down the code with more digraphs
def makes_word(game, prefix, digraph_size, dictionary):
	if prefix not in dictionary:
		return False
	if type(dictionary[prefix]) is list:
		for g in game:
			if g in dictionary[prefix]:
				return True
		return False
	game_copy = list(game).remove(prefix)
	flag = False
	for g in game_copy:
		flag = makes_word(game, g, digraph_size, dictionary[prefix])
		if flag:
			return flag
	return False

# determines if there is a solution to a given game
def exists_solution(game, dictionary, word_size, digraph_size):
	for d in game:
		flag = False
		for x in game:
			if not makes_word(game, x, digraph_size, dictionary):
				return False
	if unique_solution(game, digraph_size, word_size, dictionary):
		return True
	return False

# determines the difficulty of the game. This is calculated by a ratio of the number of words
# that can be created over the number of words needed to solve the game. The idea being that the 
# more potential words there are, the more almost-solutions there are.
def get_difficulty(game, dictionary, word_size, digraph_size):
	possible_words = permutate(game, word_size/digraph_size)
	actual_words = []
	for p in possible_words:
		if find_word(dictionary, ''.join(p), digraph_size):
			actual_words.append(p)
	return (len(p) // len(game))

# generates all games with some number of input parameters. This is simply so that playing the games
# is then much faster. Because it is necessary to try all combinations in order to generate, it is quite
# time consuming so it makes more sense to simply write down a list of valid games and let it run overnight
def generate_games(digraph_size, word_size, num_digraphs):
	start = time.time()
	all_digraphs = generate_digraphs(digraph_size)
	print("Completed generating all digraphs in %f seconds" % (time.time()-start))

	start = time.time()
	all_sets = get_subsets(all_digraphs, num_digraphs)
	print("Completed generating all potential games in %f seconds" % (time.time()-start))

	dictionary = read_in(word_size, digraph_size)

	start = time.time()
	solvable_games = []
	for s in all_sets:
		if exists_solution(s, dictionary, word_size, digraph_size):
			solvable_games.append({"solution": s, "difficulty": get_difficulty(s, dictionary, word_size, digraph_size)})
	print("Completed finding all solvable games in %f seconds" % (time.time() - start))

	with open('games-%d-%d-%d.txt' % (digraph_size, word_size, num_digraphs), 'w') as gamefile:
		for game in solvable_games:
			gamefile.write(json.dumps(game) + "\n")

# finds a good game for you to play from a pre-constructed list
def choose_game(digraph_size, word_size, num_digraphs, min_difficulty):
	potential_games = []
	with open('games-%d-%d-%d.txt' % (digraph_size, word_size, num_digraphs), 'r') as gamefile:
		for each in gamefile:
			potential_games.append(json.loads(each.strip()))
	index = random.randint(0, len(potential_games)-1)
	while (potential_games[index]['difficulty'] < min_difficulty):
		index = random.randint(0, len(potential_games)-1)
	return potential_games[index]

# checks if your solution is correct
def is_winner(solution, dictionary, original, digraph_size, word_size):
	for each in original['solution']:
		if each not in solution:
			return False, "What? These aren't even the same digraphs..."
	solution_words = get_words(solution, digraph_size, word_size)
	for word in solution_words:
		if not find_word(dictionary, word, digraph_size):
			return False, "Are you kidding?! %s isn't a real word!" % word
	return True, "CONGRATULATIONS! Your parents must be so proud."

# play the game :)
def play_game(digraph_size, word_size, num_digraphs, min_difficulty):
	dictionary = read_in(word_size, digraph_size)
	game = choose_game(digraph_size, word_size, num_digraphs, min_difficulty)
	random.shuffle(game['solution'])
	printout = ' '.join(game['solution'])
	print(printout)

	isWon = False
	while not isWon:
		guess = raw_input("Solution: ")
		guess = (guess.upper().split(' '))
		isWon, message = is_winner(guess, dictionary, game, digraph_size, word_size)
		print(message)


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Creates and plays the Digraph Puzzle Game!",
		epilog='''The goal of the game is to rearrange the n-graphs such that the digraphs spell out words!
				
				Example:
				2-graphs, 4-words, 4-letters

				AL ME TO FU

				rearranged becomes:

				ME AL TO FU

				with the words being MEAL, ALTO, TOFU, FUME

				''')

	parser.add_argument('option')
	parser.add_argument('-d', '--digraph_size', help='The size n-graph you would like to play with. Defaults to 2.')
	parser.add_argument('-n', '--num_digraphs', help='The number of n-graphs you would like to play with. Defaults to 6.')
	parser.add_argument('-w', '--word_size', help='The length of the words. Defaults to 4. Must be divisible by the size of n-graphs')
	parser.add_argument('-l', '--level', help='The difficulty level. Defaults to 1')

	args = parser.parse_args()

	if args.option == 'generate':
		start =time.time()
		generate_games(int(args.digraph_size), int(args.word_size), int(args.num_digraphs))
		print("Complete! Time to finish: ")
		print(time.time()-start)
	elif args.option == 'play':
		play_game(int(args.digraph_size), int(args.word_size), int(args.num_digraphs), int(args.level))
