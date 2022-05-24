#include <stdio.h>
#include <stdlib.h>

int main()
{
    srandom(11235813);
    for ( int i = 0; i <= 9; ++i )
    {
        printf("%c", (rand() % 26) + 65);
    }

    printf("\n");

    return 0;
}

