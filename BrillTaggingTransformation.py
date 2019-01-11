import sys
from collections import defaultdict
import copy

def readData(words, word_tags_count):

    filename = "HW2_S18_NLP6320_POSTaggedTrainingSet-Windows.txt"
    gold_corpus = open(filename, 'r').read()
    word_tags = list(gold_corpus.split())
    word_counts = {}
    word_tag_options=defaultdict(set)
    for x in word_tags:
        temp = x.split("_")
        words.append(temp[0])
        if temp[0] in word_counts:
            word_counts[temp[0]] += 1
        else:
            word_counts[temp[0]] = 1
        word_tag_options[temp[0]].add(temp[1])

    for x in word_tags:
        if x in word_tags_count:
            word_tags_count[x] += 1
        else:
            word_tags_count[x] = 1

    return word_tags, word_counts,word_tag_options


def probableTag(word_counts,word_tags_count):

    word_tags_probabilities = {}
    for x in word_tags_count:
        word = x.split("_")
        word_tags_probabilities[x] =  float(word_tags_count[x]) / float(word_counts[word[0]])
    return word_tags_probabilities

def initialTag(word_tags, words, word_tag_probabilities, word_tag_options):

    error_words = defaultdict(list)

    file1 = open("initial_tagging.txt","wt")
    prob_word_tags=[]
    for i in range(0,len(words)):
            tags = list(word_tag_options[words[i]])
            tag = tags[0]
            prob = word_tag_probabilities[words[i] + "_" + tag]
            for x in tags:
                if prob < word_tag_probabilities[words[i] + "_" + x]:
                    prob = word_tag_probabilities[words[i] + "_" + x]
                    tag = x
            prob_word_tags.append(words[i] + "_" + tag)
            file1.write(words[i]+"_"+tag+" ")
            if(words[i]=="."):
                file1.write("\n")
            actual_tag=word_tags[i].split("_")
            if actual_tag[1] != tag:
                error_words[i].append(actual_tag[1])
                error_words[i].append(tag)
    file1.close()
    return error_words, prob_word_tags

def generateTransformationRules(words, prob_word_tags, error_words, word_tags):
    rules = defaultdict(set)
    final_rules={}
    final_rules1={}
    for x in error_words:
        prev_word_tag = prob_word_tags[x-1].split("_")
        rules[prev_word_tag[1]].add(error_words[x][1] + "_" + error_words[x][0])

    rule_list=[]
    counter = 0

    print("checking the rule accuracy please wait.....")
    for x in rules:
        for y in rules[x]:
            counter += 1
            tp = y.split("_")
            ac_count=accuracy(x,tp[0],tp[1],prob_word_tags,word_tags)
            rule_list.append(tuple((x,tp[0],tp[1],ac_count)))


    rule_list = sorted(rule_list, key=lambda x : x[3])

    rule_list.reverse()



    file1 = open("Rules for NN to VB.csv","wt")
    file2 = open("RUles for VB to NN.csv", "wt")
    file1.write("Previous Word Tag" + "," + "," + "From" + "," + "," + "To"+"," + "," + "Accuracy Count")
    file2.write("Previous Word Tag" + "," + "," + "From" + "," + "," + "To" + "," + "," + "Accuracy Count")
    file1.write("\n")
    file2.write("\n")
    for x in rule_list:

        if (x[1] == "NN" and x[2] == "VB" and x[3] > -111):
            file1.write(str(x))
            file1.write("\n")

        if (x[1] == "VB" and x[2] == "NN" and x[3] > 3):
            file2.write(str(x))
            file2.write("\n")


    file1.close()
    return final_rules1

def accuracy(prev_word_tag_in_rule , from_tag_in_rule ,to_tag_in_rule , prob_word_tags , word_tags):
    copy_prob_word_tags=copy.deepcopy(prob_word_tags)
    poscount=0
    negcount=0
    for i in range(1,len(copy_prob_word_tags)):
        previous_word_tag_prob=prob_word_tags[i-1].split("_")
        current_word_tag_prob=prob_word_tags[i].split("_")
        current_actual_word_tag=word_tags[i].split("_")
        if previous_word_tag_prob[1] == prev_word_tag_in_rule:
            if current_word_tag_prob[1] == from_tag_in_rule:
                if to_tag_in_rule == current_actual_word_tag[1]:
                    poscount += 1
                elif from_tag_in_rule == current_actual_word_tag[1] and to_tag_in_rule!=current_actual_word_tag:
                    negcount += 1
    return poscount-negcount

def apply(final_rules,original_sentence, word_tag_options, word_tag_probs):
    words=original_sentence.split()
    sentence_tags_probs=[]
    for x in words:
            tags = list(word_tag_options[x])
            tag = tags[0]
            prob = word_tag_probs[x + "_" + tag]
            for y in tags:
                if prob < word_tag_probs[x + "_" + y]:
                    prob = word_tag_probs[x + "_" + y]
                    tag = y
            sentence_tags_probs.append(x + "_" + tag)
    print("Tagged sentence without appying rules:")
    print(str(sentence_tags_probs))
    for k in range(1,len(sentence_tags_probs)):
            prev_word_tags=sentence_tags_probs[k-1].split("_")
            current_word_tags=sentence_tags_probs[k].split("_")
            if (prev_word_tags[1]+"_"+current_word_tags[1]) in final_rules:
                  sentence_tags_probs[k]=(current_word_tags[0] +"_" +final_rules[prev_word_tags[1]+"_"+current_word_tags[1]])

    taggedsentence=""
    for x in sentence_tags_probs:
        taggedsentence += x + " "
    print("Tagged sentence after appying the brill's rules")
    return taggedsentence

#Implementing Naive bAyes function

def get_tag_count(word_tags):
    tag_count = {}
    for x in word_tags:
        temp=x.split("_")
        if temp[1] in tag_count:
            tag_count[temp[1]] +=1
        else:
            tag_count[temp[1]] = 1
    print(tag_count)
    return tag_count

def countFirstProbability(word_tag_count,tag_count):
    prob_word_given_tag={}
    for x in word_tag_count:
        temp = x.split("_")
        prob_word_given_tag[x] = (float) (word_tag_count[x]/ tag_count[temp[1]])

    print(prob_word_given_tag)
    return prob_word_given_tag

def countSecondProbability(word_tags,tag_count):
    prob_tag_given_tag = {}
    count_tag_given_tag ={}
    for i in range(1,len(word_tags)):
        current_tag=word_tags[i].split("_")
        prev_tag=word_tags[i-1].split("_")
        if (prev_tag[1]+"_"+current_tag[1]) in count_tag_given_tag:
            count_tag_given_tag[prev_tag[1]+"_"+current_tag[1]] += 1
        else:
            count_tag_given_tag[prev_tag[1]+"_"+current_tag[1]] = 1
    for x in count_tag_given_tag:
        prevo_tag=x.split("_")
        prob_tag_given_tag[x]= float(count_tag_given_tag[x])/float(tag_count[prevo_tag[0]])
    print(prob_tag_given_tag)
    return prob_tag_given_tag

def main():
	    words = []
	    word_tags_count = {}
	    word_tags, word_counts, word_tag_options = readData(words, word_tags_count)
	    word_tag_probabilities=probableTag(word_counts,word_tags_count)
	    error_words, prob_word_tags = initialTag( word_tags,words,word_tag_probabilities ,word_tag_options)
	    sentence = "The president wants to control the board 's control"
	    final_rules = generateTransformationRules(words, prob_word_tags, error_words ,word_tags)
	    tagged_sentence = apply(final_rules,sentence,word_tag_options, word_tag_probabilities)
	    print(tagged_sentence)
            print("\n")
            print ("Starting Naive bayes")
            tag_count = get_tag_count(word_tags)
            total_tags = len(words)
            prob_word_given_tag = countFirstProbability(word_tags_count, tag_count)
            prob_tag_given_tag = countSecondProbability(word_tags, tag_count)


main()
