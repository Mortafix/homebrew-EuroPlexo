# EuroPlexo ITA

Script in Python per scaricare automaticamente e in background le nuove puntate di serie tv, in cartelle specifiche e ordinate. Compatibile con Plex e altri sistemi di Media Center.

## Installazione
A breve su Homebrew.

## Setup
1. Inizializzare la configurazione con il comando `europlexo --config`
2. Aggiungere le serie tv desiderate, in 3 modi:
	* Scan automatico della vostra cartella delle serie tv `europlexo --scan`  
	* Aggiunta guidata con ricerca automatica della serie tv `europlexo --add-auto`
	* Aggiunta guidata manuale della serie tv `europlexo --add-man`  

**Attenzione**  
Per la scansione automatica, la configurazione della cartella deve rispettare la [Struttura Cartella](#folder-structure).

## Automatizzazione (Crontab)
Per far girare lo script in maniera automatica, bisonga aggiungere un [Crontab]() con il task. Ogni riga di crontab ha 6 argomenti (5 per il datetime e 1 per il comando)  
```bash
min hour month year day command
30 0,8,16,20 * * * command # ['command' viene eseguito alle 0.30, 8.30, 16.30, 20.30 di ogni giorno]
0 * * * * command # ['command' viene eseguito ogni ora di ogni giorno]
```
In aggiunta, un breve [video tutorial](https://www.loom.com/share/9ac5d5f25ea2490b879d1ec7b5bc0d60) sulla creazione di un task crontab.

## Folder Structure
Per la scansione automatica, la cartella delle serie tv (che possiedi già) dovrà rispettare il seguente modello.
L'unica accezione è il nome dei singoli episodi che dovranno comunque inziare con il numero dell'episodio (Es. `XX. nome_file_random.rnd`)
```bash
TV_Series_Folder
	Arrow
		Stagione 1
			01. Arrow_LaFrecciaVerde_MUX_DL-S1E01.mp4
			02. Arrow_FailThisCity_ITASUB.avi
			03. Arrow-megaupload-rip.mkv
		Stagione 2
			1.  Arrow_TheComeback_2x1.wmv
			2.  Arrow_End-FULLRIP_1080.flv  
	The Flash
		Stagione 5
			01. Flash.mpg
			2.  Arrow-LoSoCheNonSonoArrow-MaFlash42x42.swf
```

## Sites Compatibility
1. [ES](http://www.eurostreaming.pet/)
