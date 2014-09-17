for %%w in (1 2 3 4 5 6 7 8 9 10 11 12) do (
	for %%t in (POI MP LP) do (
		D:\NLP\senna\senna-win32.exe -path D:\NLP\senna\ < ..\data\senna\senna.%%w.ta.%%t.input > ..\data\senna\senna.%%w.ta.%%t.output
	)
)