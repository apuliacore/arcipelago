from telegram import ReplyKeyboardMarkup
from event import category2emoji


yes_or_no = ReplyKeyboardMarkup(
	[["Sì", "No"]], 
	one_time_keyboard=True, 
	input_field_placeholder="Sì o no?"
	)

category = ReplyKeyboardMarkup(
	[[emoji + " " + category] for category, emoji in category2emoji.items()], 
	one_time_keyboard=True, 
	input_field_placeholder="Scegli una categoria..."
	)

editable = ReplyKeyboardMarkup(
	[[field] for field in ["Nome", "Luogo", "Data inizio", "Data fine", "Ora inizio", "Ora fine", "Descrizione"]],
	one_time_keyboard=True,
	input_field_placeholder="Scegli cosa modificare"
	)