scales = {
        "gen_vals" : {"Nein":0, "Vielleicht":1, "Ja":2},
        "adhs_vals" : {"Nie":0, "Selten":1, "Manchmal":2, "Oft":3, "Sehr oft":4},
        "gen_scale" : {
            range(0,5):"sehr unwahrscheinlich",
            range(5,9):"möglich",
            range(9,13):"wahrscheinlich",
            range(13,17):"sehr wahrscheinlich"
            },
        "adhs_scale" : {
            range(0,10):"sehr unwahrscheinlich",
            range(10,14):"möglich",
            range(14,18):"wahrscheinlich",
            range(18,25):"sehr wahrscheinlich"
            }
}
