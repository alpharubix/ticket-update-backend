


def comments_name_tage(comment):
    zuid_dict = {"Ayush Dingane": "794754257", "Digamber Pandey": "797905419", "Gattu Pallavi": "803624812",
                 "Honnappa Dinni": "803130106","Amare Gowda":"799516479",
                 "Kavya KB": "803602793", "Namrata Srivastava": "690902818", "Sandip Kumar Jena": "786488411"
        , "Sonu  Sathyan": "799518946", "Subhasini T S": "797906908", "Sutapa Roy B": "797906916",}
    final_comment =''
    template_str = "zsu[@user:#]zsu"
    words = []
    str = comment.split(',')
    for word in str:
        if word in zuid_dict:
            formated_str = template_str.replace("#",zuid_dict[word])
            words.append(formated_str)
        else:
            words.append(word)
    final_comment = ' '.join(words)
    return final_comment