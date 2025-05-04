/*
The Newspaper Seller has the following problem: He would like to determine how many Newspapers he should buy each day in order to maximize his profits. His present method of determining the quantity of Newspaper is based upon his best guess or estimate of the daily demand for the day news.
Assume:
    P : Paper Sell  ( P  = 50 cent )
    C : Paper Cost ( C = 33 cent )
    S : Scrap Sale ( S = 5 cent )
    X : Papers Quantity
    d : Daily Demand
    Z : Daily Profit
    - Each day has its own type of day news ( Good , Fair , Poor )
--------------------------------
|Type of Newsday | Probability | Cumulative Probability | Random number Range |
|Good | 0.35 | 0.35 | 0 ≤ R < 0.35|
|Fair | 0.45 | 0.80 | 0.35 ≤ R < 0.80|
|Poor | 0.20 | 1.00 | 0.80 ≤ R ≤ 1|
--------------------------------
Each day has its own type of demand for day news. Calculate the cumulative distribution function cdf (Good), cdf(Fair), and cdf(Poor) for demand 40,50,60,70,80,90,100 for newspapers. The System should help the newspaper seller to decide how many papers should he bought to maximize his profit: Max Z(X,d).
I want to build a table that contains [Day Random D for Type, Type, Random D Demand, Demand, Revenue Sales, Excess Demand, lost Profit Excess Demand, Num of Scrap, Salvage from scrap, Daily Profit]
The Simulation based in Assumption [P : Paper Sell,C : Paper Cost,S : Scrap Sale,D: Days,x: Quantity], and probability of Types of newsday [0.35,0.45,0.20]
*/
#include<bits/stdc++.h>
using namespace std;

constexpr int days          = 30;
constexpr int quantity      = 70;
constexpr int paper_cost    = 33;
constexpr int iterations    = 10;
constexpr float scrap_sale  =  5;
constexpr float paper_sell  = 50;

/// Types of News day
constexpr float GOOD        = 0.35;
constexpr float FAIR        = 0.45;
constexpr float POOR        = 0.20;

float cumulative_prop[3] = {
    GOOD,
    GOOD + FAIR,
    GOOD + FAIR + POOR,
};

struct RD {
    float lower, upper;
} RandDist[3]{
    {0.0, GOOD - 0.01},
    {GOOD, GOOD + FAIR - 0.01},
    {GOOD + FAIR, GOOD + FAIR + POOR}
};

struct DayData {
    int day;
    double R1;
    string type;
    double R2;
    int demand;
    int revenue_sales;
    int excess_demand;
    int lost_profit_excess;
    int num_scrap;
    int salvage_scrap;
    int daily_profit;
};

int getDemand(const string& dayType, const double R) {
    if (dayType == "Good") {
        if (R < 0.03) return 40;
        if (R < 0.08) return 50;
        if (R < 0.23) return 60;
        if (R < 0.43) return 70;
        if (R < 0.78) return 80;
        if (R < 0.93) return 90;
        return 100;
    }

    if (dayType == "Fair") {
        if (R < 0.10) return 40;
        if (R < 0.28) return 50;
        if (R < 0.68) return 60;
        if (R < 0.88) return 70;
        if (R < 0.96) return 80;
        return 90;
    }

    if (dayType == "Poor") {
        if (R < 0.44) return 40;
        if (R < 0.66) return 50;
        if (R < 0.82) return 60;
        if (R < 0.94) return 70;
        return 80;
    }
    return {};
}

vector<DayData> simulate(int X, int N) {
    vector<DayData> results;
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(0.0, 1.0);

    for (int day = 1; day <= N; ++day) {
        double R1 = dis(gen);
        string type;
        if (R1 < cumulative_prop[0]) type = "Good";
        else if (R1 < cumulative_prop[1]) type = "Fair";
        else type = "Poor";

        double R2 = dis(gen);
        int demand = getDemand(type, R2);

        int revenue_sales = min(X, demand) * paper_sell;
        int excess_demand = max(demand - X, 0);
        int lost_profit_excess = excess_demand * (paper_sell - paper_cost);
        int num_scrap = max(X - demand, 0);
        int salvage_scrap = num_scrap * scrap_sale;
        int daily_profit = revenue_sales + salvage_scrap - X * paper_cost;

        DayData data = {day, R1, type, R2, demand, revenue_sales, excess_demand, lost_profit_excess, num_scrap, salvage_scrap, daily_profit};
        results.push_back(data);
    }
    return results;
}

void writeTableToFile(const vector< DayData > &results, const string filename) {
    ofstream outfile(filename);
    if (!outfile) return void (cerr << "NOOOOOOOOOOOOOOOO such File: " << filename << endl);

    outfile << "Day\t|\tR1\t|\tType\t|\tR2\t|\tDemand\t|\tRevenue\t|\tExcessD\t|\tLostProfit\t|\tScrap\t|\tSalvage\t|\tProfit\n";
    for (const auto &data: results) {
        outfile << data.day << "\t| \t"
                << fixed << setprecision(2) << data.R1 << "\t| \t"
                << data.type << "\t| \t"
                << fixed << setprecision(2) << data.R2 << "\t| \t"
                << data.demand << "\t| \t"
                << data.revenue_sales << "\t| \t"
                << data.excess_demand << "\t| \t"
                << data.lost_profit_excess << "\t| \t"
                << data.num_scrap << "\t| \t"
                << data.salvage_scrap << "\t| \t"
                << data.daily_profit << "\n";
    }
    outfile.close();
}

int main() {
    int N_large = 1000;
    vector< int > X_values = {40, 50, 60, 70, 80, 90, 100};
    double best_avg_profit = -numeric_limits< double >::max();
    int best_X = -1;

    cout << "Let's Simulate...\n";
    for (int X: X_values) {
        auto results = simulate(X, N_large);
        double total_profit = 0;

        for (const auto &data: results) total_profit += data.daily_profit;

        double avg_profit = total_profit / N_large;
        cout << "Quantity X = " << X << ", Average Profit = " << fixed << setprecision(2) << avg_profit << " cents\n";
        if (avg_profit > best_avg_profit) best_avg_profit = avg_profit, best_X = X;
    }

    cout << "\nOptimal quantity to buy: " << best_X << " newspapers\n";
    cout << "Expected avg profit: " << fixed << setprecision(2) << best_avg_profit << " cents per day\n";

    auto table_results = simulate(best_X, days);
    writeTableToFile(table_results, "newspaper_simulation.txt");

    double table_total_profit = 0;
    for (const auto &data: table_results) {
        table_total_profit += data.daily_profit;
    }
    double table_avg_profit = table_total_profit / days;
    cout << "\nAverage profit over " << days << " days with X = " << best_X << ": " << fixed << setprecision(2) <<
            table_avg_profit << " cents\n";

    return 0;
}
