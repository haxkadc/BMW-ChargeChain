/*
Copyright 2020 IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
*/

package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"

	"fyne.io/fyne/app"
	"fyne.io/fyne/canvas"
	"fyne.io/fyne/widget"
	"github.com/hyperledger/fabric-sdk-go/pkg/core/config"
	"github.com/hyperledger/fabric-sdk-go/pkg/gateway"
)

func main() {
	c := make(chan string)

	go funzione(c)
	myApp := app.New()
	myWindow := myApp.NewWindow("Entry Widget")
	var arg string = ""
	var comando string = "Invia"
	input := widget.NewEntry()
	content2 := widget.NewLabel("Inserire i seguenti comandi:\n1)'Get' per visualizzare tutte le colonne\n2)Read per visualizzare una determinata colonna\n3)'Noleggia' per noleggiare una colonna\n4)'Disdici' per disdire una colonna\n5)'City' per visualizzare le colonne disponibili in una determinata città,Per visualizzarle tutte digitare 'ALL'\n6)'Menu' per visualizzare di nuovo il Menu\n7)'Crea' per aggiungere una nuova colonna\n8)'Elimina' per rimuovere una colonna")
	input.SetPlaceHolder("Enter text...")
	content := widget.NewVBox(input, widget.NewButton(comando, func() {
		arg = string(input.Text)
		c <- arg
		input.SetText("")
		var result = <-c
		var tot string = ""

		z := strings.Split(result, "}")
		for _, s := range z {
			tot = tot + s + "}\n"

		}
		tot = tot[:len(tot)-2]

		content2.SetText(tot)

	}))
	image := canvas.NewImageFromFile("img.png")
	image.FillMode = canvas.ImageFillOriginal
	var group = widget.NewGroup("Gruppo", content, content2, image)
	myWindow.SetContent(group)
	myWindow.ShowAndRun()

}
func funzione(c chan string) {
	log.Println("============ application-golang starts ============")

	err := os.Setenv("DISCOVERY_AS_LOCALHOST", "true")
	if err != nil {
		log.Fatalf("Error setting DISCOVERY_AS_LOCALHOST environemnt variable: %v", err)
	}

	wallet, err := gateway.NewFileSystemWallet("wallet")
	if err != nil {
		log.Fatalf("Failed to create wallet: %v", err)
	}

	if !wallet.Exists("appUser") {
		err = populateWallet(wallet)
		if err != nil {
			log.Fatalf("Failed to populate wallet contents: %v", err)
		}
	}

	ccpPath := filepath.Join(
		"..",
		"..",
		"test-network",
		"organizations",
		"peerOrganizations",
		"org1.example.com",
		"connection-org1.yaml",
	)

	gw, err := gateway.Connect(
		gateway.WithConfig(config.FromFile(filepath.Clean(ccpPath))),
		gateway.WithIdentity(wallet, "appUser"),
	)
	if err != nil {
		log.Fatalf("Failed to connect to gateway: %v", err)
	}
	defer gw.Close()

	network, err := gw.GetNetwork("mychannel")
	if err != nil {
		log.Fatalf("Failed to get network: %v", err)
	}
	contract := network.GetContract("BMW")

	result, err := contract.EvaluateTransaction("AssetExists", "Colonna1")
	if err != nil {
		log.Fatalf("Failed to evaluate transaction: %v\n", err)
	}
	if string(result) == "false" {

		log.Println("--> Submit Transaction: InitLedger, function creates the initial set of assets on the ledger")
		_, err := contract.SubmitTransaction("InitLedger")
		if err != nil {
			log.Fatalf("Failed to Submit transaction: %v", err)
		}
	}

	for {

		log.Println("Scegli Funzione")

		var scelta = <-c
		if scelta == "Menu" {
			c <- "Inserire i seguenti comandi:\n1)'Get' per visualizzare tutte le colonne\n2)Read per visualizzare una determinata colonna\n3)'Noleggia' per noleggiare una colonna\n4)'Disdici' per disdire una colonna\n5)'City' per visualizzare le colonne disponibili in una determinata città,Per visualizzarle tutte digitare 'ALL'\n6)'Menu' per visualizzare di nuovo il Menu\n7)'Crea' per aggiungere una nuova colonna\n8)'Elimina' per rimuovere una colonna"
		} else if scelta == "Crea" {
			log.Println("--> Submit Transaction: CreateAsset, Creazione Colonna")
			log.Println("Scegli ID colonna:")
			c <- string("ID")

			var id = <-c
			log.Println("Scegli nome colonna:")
			c <- string("Nome")
			var name = <-c
			log.Println("Scegli City colonna:")
			c <- string("City")
			var city = <-c
			log.Println("Scegli address colonna:")
			c <- string("address")
			var address = <-c
			log.Println("Scegli nation colonna:")
			c <- string("Nation")
			var nation = <-c
			log.Println("Scegli supplier colonna:")
			c <- string("supplier")
			var supplier = <-c
			log.Println("Scegli fee colonna:")
			c <- string("fee")
			var fee = <-c
			log.Println("Scegli Stato colonna:")
			c <- string("disp")
			var disp = <-c
			result, err := contract.SubmitTransaction("CreateAsset", id, name, city, address, nation, supplier, fee, disp)
			if err != nil {
				result = []byte("Errore in fase di creazione")
			}
			result, err = contract.EvaluateTransaction("ReadAsset", id)
			if err != nil {
				result = []byte("Errore,sei sicuro la colonna con " + id + " Esista?")
			}
			c <- string(result)
		} else if scelta == "Get" {
			log.Println("--> Evaluate Transaction: GetAllAssets, function returns all the current assets on the ledger")
			result, err := contract.EvaluateTransaction("GetAllAssets")
			if err != nil {
				result = []byte("Errore,nessuna colonna trovata")
			}
			c <- string(result)
		} else if scelta == "Read" {

			log.Println("--> Evaluate Transaction: ReadAsset, function returns an asset with a given assetID")
			log.Println("Scegli Id della colonna:")
			c <- string("ID")
			var id = <-c
			result, err := contract.EvaluateTransaction("ReadAsset", id)
			if err != nil {
				// str := string(err.Error())
				// value := strings.Split(str, "Description:")
				//log.Fatalf("Failed to evaluate transaction: %v\n", err)
				result = []byte("Errore,sei sicuro la colonna con " + id + " Esista?")
			}
			c <- string(result)

		} else if scelta == "Noleggia" {

			log.Println("--> Evaluate Transaction: Noleggia, function returns an asset with a given assetID")
			log.Println("Scegli ID della colonna:")
			c <- string("Inserisci ID")
			var id = <-c
			result, err := contract.SubmitTransaction("Noleggia", id)
			if err != nil {
				result = []byte("Errore,sei sicuro la colonna con " + id + " sia Disponibile?")
			} else {

				result = []byte("Colonna " + id + " noleggiata")
			}
			c <- string(result)

		} else if scelta == "Disdici" {

			log.Println("--> Evaluate Transaction: Disdici, function returns an asset with a given assetID")
			log.Println("Scegli ID della colonna:")
			c <- string("Inserisci ID")
			var id = <-c
			result, err := contract.SubmitTransaction("Disdici", id)
			if err != nil {
				result = []byte("Errore,sei sicuro la colonna con " + id + " sia Noleggiata?")
			} else {
				result = []byte("La Colonna " + id + " ora di nuovo disponibile ")
			}
			c <- string(result)

		} else if scelta == "City" {

			log.Println("--> Evaluate Transaction: Disdici, function returns an asset with a given assetID")
			log.Println("Scegli la città per vedere le colonne disponibili in quella zona,All se vuoi vederle tutte)")

			c <- string("Inserisci City")
			var city = <-c
			result, err := contract.EvaluateTransaction("GetAssetsDisponibilibyCity", city)
			if err != nil {
				log.Fatalf("Failed to evaluate transaction: %v\n", err)
			}
			c <- string(result)

		} else if scelta == "Esiste" {
			log.Println("--> Evaluate Transaction: AssetExists, function returns 'true' if an asset with given assetID exist")
			log.Println("Scegli Id della colonna:")
			c <- string("ID")

			var id = <-c
			result, err := contract.EvaluateTransaction("AssetExists", id)
			if err != nil {
				result = []byte("Errore,sei sicuro la colonna con " + id + " Esista?")
			}
			c <- string(result)

		} else if scelta == "Elimina" {
			log.Println("--> Evaluate Transaction: AssetExists, function returns 'true' if an asset with given assetID exist")
			log.Println("Scegli Id della colonna:")
			c <- string("ID")
			var id = <-c
			result, err := contract.SubmitTransaction("DeleteAsset", id)
			if err != nil {
				result = []byte("Errore,sei sicuro la colonna con " + id + " Esista?")
			}
			result = []byte("Colonna eliminata")
			c <- string(result)
		} else {
			c <- "Comano non trovato, digita 'Menu' per visualizzare i comandi disponibili"
		}
	}

}
func populateWallet(wallet *gateway.Wallet) error {
	log.Println("============ Populating wallet ============")
	credPath := filepath.Join(
		"..",
		"..",
		"test-network",
		"organizations",
		"peerOrganizations",
		"org1.example.com",
		"users",
		"User1@org1.example.com",
		"msp",
	)

	certPath := filepath.Join(credPath, "signcerts", "User1@org1.example.com-cert.pem")
	// read the certificate pem
	cert, err := ioutil.ReadFile(filepath.Clean(certPath))
	if err != nil {
		return err
	}

	keyDir := filepath.Join(credPath, "keystore")
	// there's a single file in this dir containing the private key
	files, err := ioutil.ReadDir(keyDir)
	if err != nil {
		return err
	}
	if len(files) != 1 {
		return fmt.Errorf("keystore folder should have contain one file")
	}
	keyPath := filepath.Join(keyDir, files[0].Name())
	key, err := ioutil.ReadFile(filepath.Clean(keyPath))
	if err != nil {
		return err
	}

	identity := gateway.NewX509Identity("Org1MSP", string(cert), string(key))

	return wallet.Put("appUser", identity)
}

/*
func send(scelta string, c chan string) string {
	c <- scelta
	var result = <-c

	return result
}
*/
