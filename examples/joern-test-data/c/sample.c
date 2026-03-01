/**
 * Sample C code for Joern CPG analysis testing
 * Demonstrates: functions, structs, pointers, control flow
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Struct definition
typedef struct {
    int id;
    char name[64];
    float balance;
} Account;

// Function declarations
Account* create_account(int id, const char* name, float initial_balance);
void deposit(Account* account, float amount);
float withdraw(Account* account, float amount);
void print_account(const Account* account);
void free_account(Account* account);

// Create a new account
Account* create_account(int id, const char* name, float initial_balance) {
    Account* account = (Account*)malloc(sizeof(Account));
    if (account == NULL) {
        return NULL;
    }
    account->id = id;
    strncpy(account->name, name, sizeof(account->name) - 1);
    account->name[sizeof(account->name) - 1] = '\0';
    account->balance = initial_balance;
    return account;
}

// Deposit money into account
void deposit(Account* account, float amount) {
    if (account != NULL && amount > 0) {
        account->balance += amount;
    }
}

// Withdraw money from account
float withdraw(Account* account, float amount) {
    if (account == NULL || amount <= 0) {
        return 0.0f;
    }
    if (account->balance >= amount) {
        account->balance -= amount;
        return amount;
    }
    return 0.0f;
}

// Print account details
void print_account(const Account* account) {
    if (account != NULL) {
        printf("Account #%d: %s, Balance: %.2f\n",
               account->id, account->name, account->balance);
    }
}

// Free account memory
void free_account(Account* account) {
    free(account);
}

// Main function
int main(int argc, char* argv[]) {
    Account* acc = create_account(1001, "John Doe", 1000.0f);

    if (acc != NULL) {
        print_account(acc);
        deposit(acc, 500.0f);
        print_account(acc);

        float withdrawn = withdraw(acc, 200.0f);
        printf("Withdrawn: %.2f\n", withdrawn);
        print_account(acc);

        free_account(acc);
    }

    return 0;
}
