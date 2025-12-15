import random

def bull_head(card_num):
    """
    Returns the bull score (weight) for a specific card.
    """
    if card_num == 55:
        return 7
    elif (card_num % 11) == 0:
        return 5
    elif (card_num % 10) == 0:
        return 3
    elif (card_num % 5) == 0:
        return 2
    else:
        return 1

def player_point(row):
    """
        Calculate sum of bull score for each player 
    """
    total = 0
    for card in row:
        total = total + bull_head(card)
    return total

def find_best_row(card, current_row):
    """
        Where the card could take place
    """
    best_row_index = -1 #Assume card can't place
    min_diff = 105 #Make it larger than game rule

    for i, row in enumerate(current_row):
        # print(i ,row)
        last_card = row[-1]
        if card > last_card:
            diff = card - last_card
            if diff < min_diff:
                min_diff  = diff
                best_row_index = i

    return best_row_index

def restart_row(player_name, current_row, player_type):
    """
        If card can't put on the table then restart a row and make it be a first card.
        This card is -1 (output from find_best_row())
    """
    #Human side
    if player_type == "human":
        print(f"{player_name} need to restart a card row")
        for i, row in enumerate(current_row):
            point = player_point(row)
            print(f"Row:{i+1} ({point} pts): {row}")
        while True:
            choice = int(input("Choose 1 Row (1-4)")) -1
            print(f"{player_name} Chose {choice}")
            return choice
        
    #AI side
    else:
        #Use Basic Greedy to choose
        min_point = 1000
        best_row = 0
        for i, row in enumerate(current_row):
            point = player_point(row)
            if point < min_point:
                min_point = point
                best_row = i
        #print(f"{player_name} Chose {best_row+1}")
        return best_row

# def ai_select_card(hand, current_rows):
#     min_point = 1000
#     best_row = 0
#     for i, row in enumerate(current_rows):
#         point = player_point(row)
#         if point < min_point:
#             min_point = point
#             best_row = i

#     ai_card = []

#     for j in hand:
#         best_case = find_best_row(j, current_rows)

#         if best_row == best_case:
#             ai_card.append(j)
#     return ai_card

def ai_select_card(hand, current_rows):
    """
    Selects the best card from hand to minimize potential penalty.
    """
    best_card = -1
    
    min_damage = 2000 
    min_diff = 2000

    min_board_damage = 2000
    for row in current_rows:
        pts = player_point(row)
        if pts < min_board_damage:
            min_board_damage = pts

    for card in hand:
        row_index = find_best_row(card, current_rows)
        current_damage = 0
        current_diff = 0

        if row_index == -1:
            current_damage = min_board_damage
            current_diff = 1000 
        else:
            target_row = current_rows[row_index]
            current_diff = card - target_row[-1]

            if len(target_row) == 5:
                current_damage = player_point(target_row)
            else:
                current_damage = 0

        if current_damage < min_damage:
            min_damage = current_damage
            min_diff = current_diff
            best_card = card
        elif current_damage == min_damage:
            if current_diff < min_diff:
                min_diff = current_diff
                best_card = card
            elif current_diff == min_diff:
                if best_card == -1 or card < best_card:
                    best_card = card

    return best_card

def setup_game(num_name):
    # เก็บเลขที่ถูกใช้ไปแล้วทั้งหมด (ทั้งกองกลางและของผู้เล่น) เพื่อกันซ้ำ
    used_numbers = [] 
    mid_num = []
    specific_num = []

    # 1. สุ่มไพ่กองกลาง 4 ใบ
    while len(mid_num) < 4: # ใช้ while เพื่อให้ครบ 4 แน่นอน
        var = random.randint(1,104)
        if var not in used_numbers:
            mid_num.append([var]) # เก็บเป็น list ซ้อน [[var]] รอไว้เลย
            used_numbers.append(var)
        
    # 2. สุ่มไพ่ให้ผู้เล่น
    for i in range(num_name):
        hand = [] # สร้างมือเปล่าๆ สำหรับผู้เล่นคนนี้
        
        # --- จุดที่แก้: เช็คให้ครบ 10 ใบ ---
        while len(hand) < 10: # ตราบใดที่ยังไม่ครบ 10 ให้ทำต่อ
            var = random.randint(1,104)
            
            # เช็คว่าซ้ำกับที่เคยใช้ไปหรือยัง
            if var in used_numbers:
                continue # ถ้าซ้ำ ให้ข้ามไปวนลูปใหม่ (ไม่นับ)
            
            # ถ้าไม่ซ้ำ ก็ใส่ในมือ และจดลงบันทึก
            hand.append(var)
            used_numbers.append(var)
        # -------------------------------
        
        specific_num.append(hand)

    return mid_num, specific_num

def play_game():
    # 1. Setup เกม
    # mid_num คือไพ่กองกลาง 4 ใบ, specific_num คือไพ่ในมือผู้เล่น (Index 0=Human, 1=AI)
    mid_num, specific_num = setup_game(2) 
    
    # ไพ่ในมือ
    human_hand = sorted(specific_num[0]) # เรียงไพ่ในมือให้ดูง่าย
    ai_hand = sorted(specific_num[1])
    
    # คะแนนเริ่มต้น
    scores = {"Human": 0, "AI": 0}

    print("=== Game Start! ===")

    # 2. เริ่มวนลูป 10 รอบ (ตามจำนวนไพ่)
    for turn in range(1, 11):
        print(f"\n--- Turn {turn}/10 ---")
        
        # แสดงสถานะกระดานปัจจุบัน
        print("Current Rows:")
        for i, row in enumerate(mid_num):
            print(f"Row {i+1}: {row}")

        # --- Phase 1: ผู้เล่นเลือกไพ่ (Selection) ---
        
        # 1.1 Human เลือก
        print(f"\nYour Hand: {human_hand}")
        while True:
            try:
                # ให้ใส่เลขไพ่ที่จะลง (ไม่ใช่ Index) เพื่อความไม่งง
                card_val = int(input("Choose card number to play: "))
                if card_val in human_hand:
                    human_card = card_val
                    human_hand.remove(card_val) # เอาไพ่ออกจากมือ
                    break
                else:
                    print("You don't have that card!")
            except ValueError:
                print("Please enter a number.")

        # 1.2 AI เลือก (เรียกใช้ฟังก์ชัน ai_select_card ที่คุณเขียนไว้)
        ai_card = ai_select_card(ai_hand, mid_num)
        ai_hand.remove(ai_card) # เอาไพ่ออกจากมือ AI
        print(f"AI chose a card (Hidden)")

        # --- Phase 2: ประมวลผลการลงไพ่ (Processing) ---
        
        # เอาไพ่มาเรียงกัน ใครน้อยกว่าได้ลงก่อน
        # format: (card_value, owner_name)
        played_cards = sorted([(human_card, "Human"), (ai_card, "AI")], key=lambda x: x[0])

        print(f"\nResult: Human played {human_card}, AI played {ai_card}")

        for card, player_name in played_cards:
            print(f"> Processing {player_name}'s card: {card}")
            
            # หาแถวที่จะลง
            row_idx = find_best_row(card, mid_num)

            # กรณี A: ลงไม่ได้เลย (ไพ่เราเล็กกว่าทุกแถว) -> ต้องเลือกเก็บ 1 แถว
            if row_idx == -1:
                # เรียก restart_row เพื่อเลือกแถวที่จะเก็บ
                # ส่ง "human" หรือ "ai" ไปเพื่อให้ฟังก์ชันรู้ว่าต้อง input หรือ auto
                p_type = "human" if player_name == "Human" else "ai"
                chosen_row_idx = restart_row(player_name, mid_num, p_type)
                
                # คิดคะแนนจากแถวที่เลือกเก็บ
                penalty = player_point(mid_num[chosen_row_idx])
                scores[player_name] += penalty
                print(f"{player_name} takes Row {chosen_row_idx+1} (-{penalty} points)")
                
                # วางไพ่เราเป็นใบแรกของแถวใหม่
                mid_num[chosen_row_idx] = [card]

            # กรณี B: มีแถวลงได้
            else:
                target_row = mid_num[row_idx]
                
                # เช็คว่าแถวเต็มหรือยัง (ถ้ามี 5 ใบ ลงใบที่ 6 ต้องเก็บ)
                if len(target_row) == 5:
                    penalty = player_point(target_row)
                    scores[player_name] += penalty
                    print(f"Row {row_idx+1} is FULL! {player_name} takes it (-{penalty} points)")
                    
                    # เคลียร์แถว แล้ววางไพ่เราเป็นใบแรก
                    mid_num[row_idx] = [card]
                else:
                    # แถวยังไม่เต็ม ต่อท้ายได้เลย ปลอดภัย
                    target_row.append(card)
                    print(f"{player_name} put {card} at Row {row_idx+1}")

    # 3. จบเกม สรุปคะแนน
    print("\n=== Game Over ===")
    print(f"Final Scores: {scores}")
    if scores["Human"] < scores["AI"]:
        print("YOU WIN! 🎉")
    elif scores["Human"] > scores["AI"]:
        print("AI WINS! 🤖")
    else:
        print("DRAW! 🤝")

if __name__ == "__main__":
    play_game()