package idgen

import (
	"math/rand"

	"github.com/google/uuid"
)

// Generate an ID using uuid
func GenerateTxId() string {
	InstructionId := uuid.New()
	return InstructionId.String()
}

func GenerateComponentId() string {
	var letters = []rune("abcdef1234567890")
	b := make([]rune, 32)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}
