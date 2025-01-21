"""
A very simple version of the classic Animal guessing game, originally published
in various editions of David H. Ahl's _BASIC Computer Games_ books back in the
1970s.
"""

import sys

# The original program used a BASIC DATA statement to populate an array of
# strings that serve as tree nodes, and refer to each other by array indices.
# This Python version implements the same initial tree nodes using
# dictionaries. There are two kinds of nodes: question nodes, which always
# appear in the tree with two leaf nodes, and guess nodes, which are the
# leaves.
#
# Following a path through question nodes, the program asks a series of
# questions to narrow down the options, until it reaches a guess node, and
# presents an animal name to the user. If the guess is incorrect, the program
# replaces the original guess node with a new question node that has as its
# leaves the original guess node, and a new guess node created with the animal
# name the user types.
#
# In this way, as the user interacts with the program, the tree will grow. The
# original program never replaces the root node, and the tree is never
# re-balanced to minimize the number of questions it takes to get to a guess.
# "Does it swim?" is always the first question. I have kept that behavior, but
# support for re-balancing the tree would be an interesting future upgrade to
# the program.
g_node_fish = {"A":"a fish"}
g_node_bird = {"A":"a bird"}
q_node_root = {"Q":"Does it swim?",
               "Y":g_node_fish,
               "N":g_node_bird}

# Convenience functions for reading and formatting user input of various kinds.
# The original program didn't do much to clean up user input, so we don't
# either, assuming a cooperative user, but we're not as obsessed with saving
# every possible byte, so we do a few things differently:
# - We keep whatever the user types as the animal name, so you shouldn't see
#   incorrect grammar like "a octopus" unless the user typed it that way.
# - We turn animal names into lowercase, so the computer won't ask "Is it An
#   octopus." This could results in incorrect capitalization for animal names
#   containing proper nouns; for example, if the user types in "a Jack Russell
#   terrier," the guess will be "Is it a jack russell terrier?" The alternative
#   would be some kind of validation of animal names, which is out of scope for
#   this simple program.
# - We make sure that when we request a question from the user, it starts with
#   a capital letter and ends with a question mark, so if the user typed "does
#   it have four wings and fly," the question will be stored as "Does it have
#   four wings and fly?"
def get_one_word_answer() -> str:
    return sys.stdin.readline().strip().lower()

def is_answer_affirmative(answer_str:str) -> bool:
    return answer_str[0] == 'y'

def is_answer_tree(answer_str:str) -> bool:
    return answer_str[0] == 't'

def get_answer() -> str:
    return sys.stdin.readline().strip()

def get_animal() -> str:
    return get_answer().lower()

def get_question() -> str:
    q_str = get_answer().lower().capitalize()
    if q_str[-1] != '?':
        return q_str + '?'
    else:
        return q_str

def get_q_answer(new_a_str:str) -> bool:
    print('For ' + new_a_str + ', what is the answer?')
    return is_answer_affirmative(get_one_word_answer())

# Make a new guess node with a new animal name.
def make_g_node() -> dict:
    print('What animal were you thinking of? ')
    return {'A':get_animal()}

# Make a new incomplete question node, with a new question to distinguish
# between the correct animal and the animal we incorrectly guessed.
def make_q_node_with_q_only(correct_a_str:str, incorrect_a_str:str) -> dict:
    print('Please type a yes-or-no question that would distinguish ' \
          + correct_a_str + \
          ' from ' + incorrect_a_str + ':')
    return {'Q':get_question(),
            'Y':None,
            'N':None}

# Complete the question node by setting the old and new guess child nodes. To
# do this we need the answer to the question that distinguishes between the
# correct animal and the animal we incorrectly guessed.
def attach_g_nodes(new_q_node:dict, incorrect_g_node:dict,
                   correct_g_node:dict) -> None:
    # Arrange the guess nodes according to whether the new animal should be
    # be reached by a "yes" answer or a "no" answer.
    if get_q_answer(correct_g_node['A']):
        new_q_node['Y'] = correct_g_node
        new_q_node['N'] = incorrect_g_node
    else:
        new_q_node['Y'] = incorrect_g_node
        new_q_node['N'] = correct_g_node

# Make a new question node, along with its children. This requires asking for
# a new animal name, a new question to distinguish between the correct animal
# and the animal we incorrectly guessed, and the answer to that question.
def make_new_q_node(q_node:dict, g_node:dict) -> dict:
    new_g_node = make_g_node()
    new_q_node = make_q_node_with_q_only(new_g_node['A'], g_node['A'])
    # Complete the question node by setting the old and new guess child nodes.
    attach_g_nodes(new_q_node, g_node, new_g_node)
    # The new question node will be inserted into the tree in place of the old
    # guess node.
    return new_q_node

# Add a new question node to the "yes" branch of an existing question node.
def insert_new_yes_branch_q_node(q_node:dict, g_node:dict):
    new_q_node = make_new_q_node(q_node, g_node)
    # Change the parent's "yes" dictionary entry.
    q_node['Y'] = new_q_node

# Add a new question node to the "no" branch of an existing question node.
def insert_new_no_branch_q_node(q_node:dict, g_node:dict):
    new_q_node = make_new_q_node(q_node, g_node)
    # Change the parent's "no" dictionary entry.
    q_node['N'] = new_q_node

# This function handles a guess node, which is always a leaf node, containing
# an animal name. If the guess is not correct, ask for the correct animal name
# and a question we can use in the future to distinguish between the two
# animals. This is how the game "learns."
def play_g_node(q_node:dict, g_node:dict, followed_yes_path:bool) -> None:
    print("Is it " + g_node['A'] + '?')
    if is_answer_affirmative(get_one_word_answer()):
        print('Great! Try another animal!')
    else:
        # Add a new question node to the existing question node's "yes" or "no"
        # branch, depending on the path we took to reach the guess node.
        if followed_yes_path:
            insert_new_yes_branch_q_node(q_node, g_node)
        else:
            insert_new_no_branch_q_node(q_node, g_node)

# This function handles any pair of parent and child nodes once we've asked at
# least one question, and so know if we're following the "yes" branch or not.
# Gameplay proceeds with mutual recursion between the pair of functions
# play_q_node() and play_node() until a guess node is reached.
def play_node(q_node:dict, node:dict, followed_yes_path:bool) -> None:
    if (node.get('Q')):
        play_q_node(node)
    else:
        play_g_node(q_node, node, followed_yes_path)

# This function handles any question node including the root. Ask the question,
# and then we know whether we're following the "yes" branch or not, and can
# call play_node().
def play_q_node(q_node) -> None:
    print(q_node['Q'])
    if is_answer_affirmative(get_one_word_answer()):
        play_node(q_node, q_node["Y"], True)
    else:
        play_node(q_node, q_node["N"], False)

def play_game(root_q_node:dict) -> None:
    # The root node is always a question node.
    play_q_node(root_q_node)

def get_indent_str(level) -> str:
    return " " * level * 3

# This is a pre-order, depth-first binary tree traversal in disguise. The basic
# algorithm is expressed something like this (in pseudocode):
#
# function handle_node(node)
#     do_something(node)
#     handle_node(node.left)
#     handle_node(node.right) 
#    
# Our traversal to print the game tree differs in the following ways:
#
# - We have two types of nodes, and they are handled differently, rather than
#   the usual design in which all nodes are the same type, and leaf nodes have
#   null left and right child pointers or references.
#
# - We report the current node question before each recursive call to handle
#   the left and right subtrees (in our case, the "yes" and "no" subtrees),
#   instead of just once before both calls. This is to make it clearer which
#   combination of question and answer brings us to each question or guess
#   node, because when printing a large tree there can be a large number of
#   lines from the subtrees printed between the two branches of a question
#   node.
#
# - We have a level parameter, used for indentation.
def print_game_tree(node:dict, level:int):
    if (node.get('Q')):
        print(get_indent_str(level) + 'Question: ' + node['Q'] + ' -> yes:')
        print_game_tree(node['Y'], level + 1)
        print(get_indent_str(level) + 'Question: ' + node['Q'] + ' -> no:')
        print_game_tree(node["N"], level + 1)
    else:
        print(get_indent_str(level) + "Guess: " + node['A'])
    return

print()
print('Play "Guess the Animal." Think of an animal and the computer will')
print('attempt to guess it. The game gets smarter over time as you teach it')
print('about more animals! This program by Paul R. Potts is based on the')
print('original BASIC game as it appears in the book Basic Computer Games:')
print('TRS-80 Edition, edited by David H. Ahl.')
print()
print('If you would like to see the internal tree of questions and animal')
print('names, type "tree" instead of "yes" or "no" when the program asks')
print('"Are you thinking of an animal?"')

while True:
    print()
    print('Are you thinking of an animal?')
    answer_str = get_one_word_answer()
    if is_answer_affirmative(answer_str):
        # Note that the root node is never replaced; the initial question is
        # always the same. Therefore, we don't need to pass a parent node to.
        # play_root().
        play_game(q_node_root)
    elif is_answer_tree(answer_str):
        print("Game tree:")
        print_game_tree(q_node_root, 1)
    else:
        print("Goodbye for now!")
        break