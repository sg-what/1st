
def decide_bid_vs_ask():
    return 1


def get_suggestion_past_trx(data, trx:int):
    """
        data should contain information symbol, bid, ask, price, volume of # last trx
        v= how many % volume increase compare to -1
        p= how many % price increase compare to -1
        m= how many % bid vs ask
        b= how many % bid increase compare to -1
        a= how many % ask increase compare to -1
        
        buy optimistics :
            (v * b) / m
        -- need to find optimistics
        -- suggestion (buy, sell, hold)

        t= (v+p+m+b+a) * #trx
    """
    # buy higher
    for i 
