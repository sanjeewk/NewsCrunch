from pydoc import text
#from spacy.lang.en.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
import en_core_web_sm
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from nltk import tokenize
STOP_WORDS = ['via', 'but', 'latter', 'not', 'then', 'upon', 'whom', 'a', 'also', 'some', 'give', 'put', 'used', 'last', 'bottom', 'anyhow', 'among', 'hereby', 'sometimes', 'seem', 'ever', 'never', 'full', 'are', 'anyone', 'made', 'beside', 'during', 'while', 'must', 'somewhere', 'anything', 'too', 'it', 'now', 'thereupon', 'thereby', 'serious', "'s", 'though', 'doing', 'more', 'whereupon', 'top', '’m', 'as', 'this', 'amongst', 'and', 'again', 'other', 'nothing', 'we', 'yet', 'call', 'would', '’re', 'that', 'into', 'therefore', 'elsewhere', 'down', 'should', 'everywhere', 'something', 'here', 'thru', 'just', 'these', 'hers', 'herein', 'everything', 'former', 'be', 'alone', 'take', 'third', 'see', 'whenever', 'another', 'below', 'often', 'using', 'move', 'formerly', 'were', 'which', 'one', 'less', "'re", 'either', 'becoming', 'himself', 'somehow', 'still', 'otherwise', 'nobody', 'seeming', 'is', 'off', 'your', 'yours', 'n’t', 'toward', 'being', 'up', 'make', 'whereafter', 'what', 'any', 'by', 'the', "'ve", 'do', 'because', 'go', 'show', 'own', 'sixty', 'eleven', '‘re', 'can', '‘ve', '’d', 'five', 'noone', 'before', 'ours', 'say', 'since', 'first', 'yourself', '‘s', 'back', 'will', 'really', 'why', 'those', 'therein', 'nevertheless', 'fifty', 'our', 'hereafter', 'to', 'whose', 'or', 'n‘t', 'always', 'ourselves', 'done', 'else', 'hence', 'on', 'its', 'every', 'me', 'throughout', 'whole', 'someone', 'twenty', 'per', 'how', 'themselves', 'his', 'keep', "'m", 'ten', 'without', '’ll', 'no', 'beforehand', 'myself', 'wherein', 'does', 'i', 'hundred', 'from', 'becomes', 'besides', 'against', 'yourselves', 'thereafter', 'about', 'none', 'with', 'together', 'until', "'ll", 'few', 'almost', 'itself', "'d", 'across', 'due', 'anywhere', 'became', 'next', 'in', 'although', 'above', 'side', 'whether', 'everyone', '’ve', 'seems', 'my', 'nowhere', 'two', 'whatever', 'twelve', 'ca', 'namely', 're', 'you', 'amount', 'further', 'under', 'anyway', 'may', 'when', 'cannot', 'sometime', 'six', '‘ll', 'where', 'regarding', 'except', 'than', 'same', 'all', 'various', 'them', 'even', "n't", 'after', 'there', 'have', 'quite', 'was', 'only', 'whereas', 'very', 'whence', 'whoever', 'over', 'an', 'once', 'around', 'beyond', 'empty', 'within', 'perhaps', 'forty', 'much', 'both', 'least', 'nor', 'herself', 'name', 'wherever', 'meanwhile', 'each', 'latterly', 'mostly', 'moreover', 'such', 'rather', 'front', 'us', 'indeed', 'thus', 'well', 'for', 'unless', 'behind', 'so', 'has', 'if', 'could', 'several', 'become', 'nine', 'enough', 'through', 'she', 'many', 'her', 'whereby', 'might', 'whither', 'thence', 'he', 'mine', 'had', 'three', 'fifteen', 'am', 'afterwards', 'of', 'eight', 'most', 'who', 'between', '‘m', 'out', 'part', 'along', 'they', 'however', 'towards', 'neither', 'did', '’s', 'been', 'onto', 'get', '‘d', 'at', 'four', 'others', 'their', 'seemed', 'him', 'please', 'hereupon', 'already']

# python -m spacy download en_core_web_sm
#  nltk.download('punkt')
class Summariser:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/bert-small2bert-small-finetuned-cnn_daily_mail-summarization")
        self.sum = pipeline(task="summarization", model=self.model, tokenizer=self.tokenizer)
        self.nlp = en_core_web_sm.load()

    def __call__(self, txt:str, summary:int=5):
        ex = self.extractive_summary(str(txt))
        ab = self.sum(ex)[0]
        return (self.grammar_check(ex,ab["summary_text"]))  
        

    def extractive_summary(self, text):
        doc = self.nlp(text)
        corpus = [sent.text.lower() for sent in doc.sents ]
        cv = CountVectorizer(stop_words=STOP_WORDS)   
        cv_fit=cv.fit_transform(corpus)    
        word_list = cv.get_feature_names_out();    
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
                summary += str(sent) + " "
            else:
                continue
        return summary

    def abstractive_summary(self, text:str):
        summary = self.sum(text)
        return self.grammar_check(text)

    def grammar_check(self, original_text:str, summarised_text:str) -> str:
        summarised_text = summarised_text.replace(" ' ", "'")
        summarised_text = summarised_text.replace("$ ", "$")
        summarised_text = summarised_text.replace(" %", "%")
        summarised_text = summarised_text.replace("( ", "(")
        summarised_text = summarised_text.replace(" )", ")")
        sentences = tokenize.sent_tokenize(summarised_text)
        sentences = [sent.capitalize() for sent in sentences]
        summarised_text = " ".join(sentences)
        or_t = self.nlp(original_text)
        sum_t = self.nlp(summarised_text)

        original_words = []
        summarised_words = []

        for tok in or_t:
            # print(tok.text)
            original_words.append(tok.text)
        for tok in sum_t:
            summarised_words.append(tok.text)
        for word in summarised_words:
            if word not in original_words:
                if word.capitalize() in original_words:
                    summarised_text = summarised_text.replace(" "+word, " "+word.capitalize())
                if word.upper() in original_words:
                    summarised_text = summarised_text.replace(word, word.upper())
            # else:
            #     print("found " + word)
        # print(vocab)
        # print(original_words)
        # print(summarised_words)

        # print(original_text)
        # print("--------------")
        print(summarised_text)
        return summarised_text

if __name__ == "__main__":
    s = Summariser()
    txt = '''The accused gunman, identified as Chunli Zhao, 67, was taken into custody a short time later after he was found sitting in his vehicle, parked outside a sheriff's station, where authorities said they believe he had come to turn himself in. A semi-automatic handgun was found in his car, San Mateo County Sheriff Christina Corpus told an evening news conference. Corpus said the suspect, who was "fully cooperating" with investigators following his arrest, had worked at one of the two crime scenes. She described the sites as agricultural "nurseries," where some of the workers also lived. Local media reported one site was a mushroom farm. In a separate Bay-area incident on Monday evening that drew far less attention, one person was killed and seven wounded in a "shooting between several individuals" in Oakland, police reported, in circumstances suggesting a case of gang violence. Police gave few details, but said the surviving victims had all gotten themselves to area hospitals. News of the massacre in Half Moon Bay surfaced as police worked through a second full day of their investigation into the shooting at the Star Ballroom Dance Studio in Monterey Park, just east of downtown Los Angeles, where a gunman shot 11 people to death. Nine others were wounded. Authorities said the suspect, Huu Can Tran, 72, drove next to an adjacent town and barged into a second dance hall but was confronted by the club's operator, who wrestled the weapon away during a brief scuffle. Tran, himself a longtime patron of the Star Ballroom, catering mainly to a older dance enthusiasts, fled again and vanished overnight.'''
    txt = '''Jan 24 (Reuters) - Paranoid? The domino downfall of FTX and other crypto custodians is enough to make the most trusting investor grab their bitcoin and shove it under the mattress. Indeed, holders big and small are taking "self-custody" of their funds, moving them from crypto exchanges and trading platforms to personal digital wallets. In a sign of this shift among retail investors, the number of bitcoin held in smaller wallets - those with under 10 bitcoin - rose to 3.35 million as of Jan. 11, up 23% from the 2.72 million held a year ago, according to data from CoinMetrics. As a percentage of total bitcoin supply, wallet addresses holding under 10 bitcoin now own 17.4%, up from 14.4% a year ago. "A lot of this really depends on how frequently you're trading," said Joshua Peck, founder of hedge fund TrueCode Capital. "If you're just going buy and hold for the next 10 years, then it's probably worth making the investment and learning how to custody your assets really, really well." The stampede has been turbocharged by the FTX scandal and other crypto collapses, with large investors leading the way. The 7-day average of daily movement of funds from centralized exchanges to personal wallets jumped to a six-month high of $1.3 billion in mid-November, at the time of FTX collapse, according to data from Chainalysis. Big investors with transfers of above $100,000 were responsible for those flows, the data showed. Not your keys, not your coins. This mantra among early crypto enthusiasts, cautioning that access to your funds is paramount, regularly trended online last year as finance platforms dropped like flies. Self-custody's no walk in the park, though. Wallets can range from "hot" ones connected to the internet or "cold" ones in offline hardware devices, although the latter typically don't appeal to first-time investors, who often buy crypto on big exchanges. The multi-level security can often be cumbersome and expensive process for a small-time investor, and there's always the challenge of guarding keeping your encryption key - a string of data similar to a password - without losing or forgetting it. Meanwhile, hardware wallets can fail, or be stolen. "It's very challenging, because you have to keep track of your keys, you have to back those keys up," said Peck at TrueCode Capital, adding: "I'll tell you it's a very challenging prospect of doing self custody for a multi-million-dollar portfolio of crypto." Institutional investors are also turning to regulated custodians - specialized companies that can hold funds in cold storage - as many traditional finance firms would not legally be able to "self-custody" investors' assets. One such firm, BitGo, which provides custodian services custody for institutional investors and traders, said it saw a 25% increase in onboarding inquiries in December versus the month before from those looking to move their funds from exchanges, plus a 20% jump in assets under custody. David Wells, CEO of Enclave Markets, said trading platforms were extremely cautious of the risks of storing the investors' assets with a third party. "A comment that stuck with me was 'investors will forgive us for losing some of their money through our trading strategies, because that's what they sign up for, what they're not going to forgive us is for being poor custodians'." Our Standards: The Thomson Reuters Trust Principles.'''
    # tst = "goldman sachs group inc ' s asset management arm will significantly reduce the $ 59 billion of alternative investments. the positions included $ 15 billion in equity investments, $ 19 billion in loans and $ 12 billion in debt securities. investors are also showing interest in private equity funds and are looking to buy positions in the secondary market."
    # txt = '''Rupert Murdoch on Tuesday withdrew a proposal to reunite News Corp (NWSA.O) and Fox Corp as the company is also exploring a sale of Move Inc, which operates the Realtor.com website, to CoStar Group, according to a regulatory filing and sources familiar with the process. Three sources familiar with the matter said News Corp was in talks to sell its stake in Move to CoStar for about $3 billion. Several top shareholders had publicly said they opposed the proposed Fox-News Corp combination, and on Tuesday News Corp said in a statement that it was "not optimal for shareholders of News Corp and Fox at this time." News Corp confirmed the talks to sell Move to CoStar after Reuters reported it on Tuesday, adding that there is no guarantee the discussions will lead to a transaction. No offer was exchanged between News Corp and Fox Corp before merger deliberations were abandoned, according to sources familiar with the process, who said pushback from News Corp shareholders played a role in those plans being scrapped. A rally in News Corp shares in recent weeks meant that Fox would have had to pay a significant premium for the merger to be agreed, something that the Murdochs did not believe they could justify to shareholders, people familiar with the matter said. Murdoch proposed reuniting his media empire last fall, arguing that together the publishing and entertainment companies he split apart in 2013 would give the combined company greater scale in news, live sports and information, sources said. In a letter to News Corp employees on Tuesday, News Corp Chief Executive Robert Thomson said: "In my note to you in October, I said the Special Committee assessment would have no impact on our current operations; that was indeed the case, and remains so following today’s announcement."'''
    f = s(txt)
