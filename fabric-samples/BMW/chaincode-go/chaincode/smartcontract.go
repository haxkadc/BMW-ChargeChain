package chaincode

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing an Asset
type SmartContract struct {
	contractapi.Contract
}

// Asset describes basic details of what makes up a simple asset
type Asset struct {
	ID       string  `json:"ID"`
	Name     string  `json:"Name"`
	City     string  `json:"City"`
	Address  string  `json:"Address"`
	Nation   string  `json:"Nation"`
	Supplier string  `json:"Supplier"`
	Fee      float32 `json:"Fee"`
	Disp     string  `json:"Disp"`
}

// InitLedger adds a base set of assets to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	assets := []Asset{
		{ID: "Colonna1", Name: "C1", City: "Napoli", Address: "via Roma", Nation: "Italy", Supplier: "Eni", Fee: 4.0, Disp: "true"},
		{ID: "Colonna2", Name: "C1", City: "Roma", Address: "via Condotti", Nation: "Italy", Supplier: "Enel", Fee: 6.0, Disp: "true"},
		{ID: "Colonna3", Name: "C1", City: "Firenze", Address: "via Duomo", Nation: "Italy", Supplier: "Illumia", Fee: 5.0, Disp: "true"},
		{ID: "Colonna4", Name: "C1", City: "Padova", Address: "via Cavour", Nation: "Italy", Supplier: "Edison", Fee: 7.0, Disp: "true"},
		{ID: "Colonna5", Name: "C1", City: "Torino", Address: "via Roma", Nation: "Italy", Supplier: "Enel", Fee: 6.0, Disp: "true"},
		{ID: "Colonna6", Name: "C1", City: "Napoli", Address: "via Bernini", Nation: "Italy", Supplier: "Edison", Fee: 7.0, Disp: "true"},
	}

	for _, asset := range assets {
		assetJSON, err := json.Marshal(asset)
		if err != nil {
			return err
		}

		err = ctx.GetStub().PutState(asset.ID, assetJSON)
		if err != nil {
			return fmt.Errorf("failed to put to world state. %v", err)
		}
	}

	return nil
}

// CreateAsset issues a new asset to the world state with given details.
func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, id string, name string, city string, address string, nation string, supplier string, fee float32, disp string) error {
	exists, err := s.AssetExists(ctx, id)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the asset %s already exists", id)
	}

	asset := Asset{
		ID:       id,
		Name:     name,
		City:     city,
		Address:  address,
		Nation:   nation,
		Supplier: supplier,
		Fee:      fee,
		Disp:     disp,
	}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, assetJSON)
}

// ReadAsset returns the asset stored in the world state with given id.
func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, id string) (*Asset, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("the asset %s does not exist", id)
	}

	var asset Asset
	err = json.Unmarshal(assetJSON, &asset)
	if err != nil {
		return nil, err
	}

	return &asset, nil
}

//Noleggia una colonna
func (s *SmartContract) Noleggia(ctx contractapi.TransactionContextInterface, id string) error {
	asset, err := s.ReadAsset(ctx, id)
	if err != nil {
		return err
	}
	if asset == nil {
		return fmt.Errorf("the asset %s does not exist", id)
	}
	if asset.Disp == "false" {
		return fmt.Errorf("Colonna %s non disponibile", id)
	}
	asset.Disp = "false"
	assetJSON, err := json.Marshal(asset)
	return ctx.GetStub().PutState(id, assetJSON)
}

//Disdici una colonna
func (s *SmartContract) Disdici(ctx contractapi.TransactionContextInterface, id string) error {
	asset, err := s.ReadAsset(ctx, id)
	if err != nil {
		return err
	}
	if asset == nil {
		return fmt.Errorf("the asset %s does not exist", id)
	}
	if asset.Disp == "true" {
		return fmt.Errorf("Colonna %s già disponibile", id)
	}
	asset.Disp = "true"
	assetJSON, err := json.Marshal(asset)

	return ctx.GetStub().PutState(id, assetJSON)
}

// DeleteAsset deletes an given asset from the world state.
func (s *SmartContract) DeleteAsset(ctx contractapi.TransactionContextInterface, id string) error {
	exists, err := s.AssetExists(ctx, id)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("the asset %s does not exist", id)
	}

	return ctx.GetStub().DelState(id)
}

// AssetExists returns true when asset with given ID exists in world state
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return assetJSON != nil, nil
}

// TransferAsset updates the owner field of asset with given id in world state.
func (s *SmartContract) TransferSupplier(ctx contractapi.TransactionContextInterface, id string, supplier string) error {
	asset, err := s.ReadAsset(ctx, id)
	if err != nil {
		return err
	}

	asset.Supplier = supplier
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(id, assetJSON)
}

func (s *SmartContract) GetAssetsDisponibilibyCity(ctx contractapi.TransactionContextInterface, city string) ([]*Asset, error) {
	// range query with empty string for startKey and endKey does an
	// open-ended query of all assets in the chaincode namespace.
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var assets []*Asset
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var asset Asset
		err = json.Unmarshal(queryResponse.Value, &asset)
		if err != nil {
			return nil, err
		}
		if asset.Disp == "true" {
			if city == "ALL" || asset.City == city {
				assets = append(assets, &asset)
			}

		}
	}

	return assets, nil
}

// GetAllAssets returns all assets found in world state
func (s *SmartContract) GetAllAssets(ctx contractapi.TransactionContextInterface) ([]*Asset, error) {
	// range query with empty string for startKey and endKey does an
	// open-ended query of all assets in the chaincode namespace.
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var assets []*Asset
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var asset Asset
		err = json.Unmarshal(queryResponse.Value, &asset)
		if err != nil {
			return nil, err
		}
		assets = append(assets, &asset)
	}

	return assets, nil
}
