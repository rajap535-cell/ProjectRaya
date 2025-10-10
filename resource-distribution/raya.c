#include <stdio.h>

int daysInMonth(int n){
    if( n == 2){
        return 28;
    }
    else if( n < 8){
        if(n%2 == 0){
            return 30;
        }
        else{
            return 31;
        }
    }
    else{
        if(n%2 == 0){
            return 31;
        }
        else{
            return 30;
        }
    }
}

int isLeapYear(int y){
    if(y%100 == 0){
        if( y%400 == 0){
                return 1;
        }
        else{
            return 0;
        }
    }
    else if(y%4 == 0){
            return 1;
    }
    else{
        return 0;
    }
}

int leapYear(int y1, int y2){
    int count = 0;
    for(int i = y1; i <= y2; i++){
        if(i%100 == 0){
            if( i%400 == 0){
                count = count +1;
            }
        }
        else if(i%4 == 0){
            count++;
        }
    }
    return count;
}

int numOfDays(int m1, int m2, int d1, int d2){
    int total = 0;
    if(m1 < m2){
        for(int i = m1; i <= m2; i++){
            if(i == m1){
                total = total + daysInMonth(i)-d1 +1;
            }
            else if( i == m2){
                total = total + d2;
            }
            else{
                total = total + daysInMonth(i);
            }
        }  
    }
    else if(m1 == m2){
        total = total + (d2 - d1);;
    }
    else{
        for(int i = m1; i != 12 ; i++){
            if(i == m1){
                total = total + daysInMonth(i)-d1 +1;
            }
            else{
                total = total + daysInMonth(i);
            }
        }
        for(int i = m2; i > 0; i--){
            if( i == m2){
                total = total + d2;
            }
            else{
                total = total + daysInMonth(i);
            }
        }
        total = total - 365;
    }
    return total;
}


int calculateDays(int d1, int d2, int m1, int m2, int y1, int y2){
    int total = 0;
    if( isLeapYear(y1) == 1 && m1 <= 2){
        if(isLeapYear(y2) == 1 && m2 > 2){
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2);
        }
        else{
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2) -1;
        }
    }
    else{
        if(isLeapYear(y2) == 1 && m2 > 2){
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2)-1;
        }
        else{
            total = total + numOfDays(m1, m2, d1, d2) + leapYear(y1, y2) -2;
        }
    } 
    total = total + (y2 - y1) * 365;
    return total;  
}

int waterDistributionPerCapitaForIndia(){
    double x = 3838.00;  
    // x = todays_expected_wateravailibity_in_litre_for_2025 according to ministey of water resources under Govt of india
    double y = 3507; 
    // y = expected_wateravailibility_in_litre_for_2035
    
    int d2, m2, y2;
    printf("\nEnter the current date (eg. if current date is 6th November 2025, given it as 6 11 2025 ) :- ");
    scanf("%d %d %d", &d2, &m2, &y2);
    int z = calculateDays(1, d2, 1, m2, 2025, y2);

    double expected_change_in_decade = x- y;
    // printf("%lf", expected_change_in_decade);

    double expecter_change_perYear = expected_change_in_decade / 10;
    double per_day_changes = (expecter_change_perYear)/365;
    double per_capita_availibility = (3838 - (per_day_changes * z));

    if(y2 < 2025 && y2 < 2036){
        printf("invalit input, Please input year ahead of 2025\n\n");
        return 0;
    }
        

    printf("Water available in India on %d/%d/%d = %.2lf", d2, m2, y2, per_capita_availibility);
    printf("litre\n");
    printf("This data is calculated on projected data by Ministry of water - Govt of India for 2035\n\n");
    return 0;
}

int population(){
    long population_2025 = 1467335156;
    long population =  population_2025;
    int population_year;
    float percentage_change[10] = {0.88, 0.87, 0.86, 0.84, 0.82, 0.78, 0.71, 0.72, 0.71, 0.71}; //yearly percentage change  given for 2026 t0 2035

    printf("which year population you want to know, Please enter that year:- ");
    scanf("%d", &population_year);

    if(population_year == 2025){
        printf("population of 2025 = %ld according to United Nation Population Devision and world Bank prediction estimates ", population);
    }

    else if(population_year < 2036 && population_year > 2025){
        for(int i = 2026; i <= population_year; i++ ){
            population = population + (population_2025 * percentage_change[population_year - 2026])/100;
        }
        printf("population of %d = %ld \nAbove data is based on United Nation Population Devision and world Bank prediction estimates \n\n", population_year, population);
    }

    else{
        printf("We don't have accurate estimate data for %d , after seeing decreasing fertility trends.", population_year);
        printf("It is estimated by national and internaional organisations population of India will start to decrease from 2060.");
        printf("So, now, We can provide data here till 2060. Thank You!\n\n");
    }
    return 0;
}

int resourceDistribution(){
    waterDistributionPerCapitaForIndia();
    population();
    return 0;
}

int main(){
    resourceDistribution();
    return 0;
}