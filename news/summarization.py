from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
import en_core_web_sm
nlp = en_core_web_sm.load()

def extractive_summary(text):
    # ta = ['March 1 (Reuters) - The U.S. Supreme Court on Tuesday wrestled with the circumstances under which doctors can be convicted of operating as drug dealers under the cover of their medical practices to illegally distribute opioid painkillers and other dangerous narcotics.', 'The justices heard arguments in an appeal by two doctors, Xiulu Ruan and Shakeel Kahn, of lower court rulings upholding their convictions on narcotics violations and related crimes stemming from what prosecutors called the misuse of medical licenses to engage in drug trafficking.', 'Lawyers for Ruan, who practiced in Alabama, and Kahn, who practiced in Arizona and then Wyoming, complained to the justices that jurors convicted the doctors of unlawfully dispensing massive amounts of opioids through "pill mill" clinics without having to weigh whether they had a "good faith" reason to believe their prescriptions were medically valid.', "Some of the justices questioned why jurors should be instructed to consider the doctors' beliefs at all about the medical validity of their prescriptions when determining if they violated a federal law called the Controlled Substances Act.", 'Chief Justice John Roberts asked "how is that different" than if police pulled over a driver on a highway for going over a 50-mile-per-hour (80 km) speed limit who then argued that the speed limit should be higher. The driver would still get ticketed, Roberts said.', 'There has been an increase in U.S. criminal prosecutions of doctors who have prescribed addictive pain pills amid a law enforcement push to combat an opioid abuse epidemic that has caused hundreds of thousands of overdose deaths over the past two decades.', "The Supreme Court took up the doctors' appeals amid divisions in lower courts about the standard under which doctors could be convicted of violating the Controlled Substances Act for writing prescriptions outside the bounds of professional practice.", "Eric Feigin, a U.S. deputy solicitor general arguing for the government, said accepting the doctors' arguments would upend the purposes of licenses issued by the U.S. Drug Enforcement Administration for doctors to prescribe dangerous drugs.", '"They want to be free of any obligation even to undertake any minimal effort to act like doctors when they prescribe dangerous, highly addictive and, in one case, lethal dosages of drugs to trusting and vulnerable patients," Feigin said.', 'Ruan was sentenced to 21 years in prison and Kahn to 25 years in separate criminal prosecutions.', 'Prosecutors said Ruan, through a clinic in Mobile, issued nearly 300,000 controlled-substance prescriptions from 2011 to 2015 and accepted kickbacks from drugmaker Insys Therapeutics Inc to prescribe a fentanyl spray to patients.', 'Prosecutors said Kahn regularly sold prescriptions for cash and unlawfully prescribed large amounts of opioid pills, resulting in at least one patient dying of an overdose.', "Lawrence Robbins, Ruan's lawyer, said that while jurors are free to disbelieve that a doctor had a good faith belief in the medical validity of their drug prescriptions, they should be instructed by courts to consider that defense before reaching a verdict.", 'Justice Samuel Alito said the Controlled Substance Act by his reading had no mention of such a requirement.', '"As for \'good faith,\' I don\'t know where that word comes from at all," Alito said.', 'Justice Brett Kavanaugh said the statute\'s requirement of a "legitimate medical purpose" to prescribe controlled substances was vague and something "on which reasonable people can disagree."', 'Kavanaugh appeared open to instructing jurors to hear good faith defenses from doctors, saying jurors would almost certainly disbelieve them if they came in with "some outlandish theory."', 'Our Standards: The Thomson Reuters Trust Principles.', 'Thomson Reuters', 'Nate Raymond reports on the federal judiciary and litigation. He can be reached at nate.raymond@thomsonreuters.com.']
    # text = ""
    # for t in ta:
    #     text +=t

    doc = nlp(text)

    corpus = [sent.text.lower() for sent in doc.sents ]
    cv = CountVectorizer(stop_words=list(STOP_WORDS))   
    cv_fit=cv.fit_transform(corpus)    
    word_list = cv.get_feature_names();    
    count_list = cv_fit.toarray().sum(axis=0)
    word_frequency = dict(zip(word_list,count_list))

    val=sorted(word_frequency.values())
    higher_word_frequencies = [word for word,freq in word_frequency.items() if freq in val[-4:]]
    # print("\nWords with higher frequencies: ", higher_word_frequencies)
    # gets relative frequency of words
    higher_frequency = val[-1]
    for word in word_frequency.keys():  
        word_frequency[word] = (word_frequency[word]/higher_frequency)

    sentence_rank={}
    for sent in doc.sents:
        for word in sent :       
            if word.text.lower() in word_frequency.keys():            
                if sent in sentence_rank.keys():
                    sentence_rank[sent]+=word_frequency[word.text.lower()]
                else:
                    sentence_rank[sent]=word_frequency[word.text.lower()]
    top_sentences=(sorted(sentence_rank.values())[::-1])
    top_sent=top_sentences[:5]

    summary=""
    for sent,strength in sentence_rank.items():  
        if strength in top_sent:
            summary.append(sent)
        else:
            continue
    # for i in summary:
    #     print(i,end=" ")
    #     print("\n")
    return summary

def abstractive_summary(text:str):