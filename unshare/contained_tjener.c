#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/wait.h> 
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <sys/mount.h>
#include <netinet/tcp.h>

#define LOKAL_PORT 80
#define BAK_LOGG 10 // Størrelse på for kø ventende forespørsler
#define BUFFER_SIZE 1024

void headerResponse(int handler, int status, int cont_len, char* mime);
void demon();

struct fileType
{
	char type[50];
};

int main()
{

	struct sockaddr_in lok_adr;
	int sd, ny_sd, validFileType;
	char buffer[BUFFER_SIZE];
	char buffer2[BUFFER_SIZE];
	//char head[1024];
	char *reqMessage;
	char *extension;
	char *mimeType;
	char *token;
	char *tmp;
	char *savePtr2;
	char *finalResponse;
	//char *mimeKeeper;

	struct fileType mime[9];

	strcpy(mime[0].type, "text/html");
	strcpy(mime[1].type, "text/plain");
	strcpy(mime[2].type, "text/css");
	strcpy(mime[3].type, "image/png");
	strcpy(mime[4].type, "image/svg");
	strcpy(mime[5].type, "application/xml");
	strcpy(mime[6].type, "application/xslt+xml");
	strcpy(mime[7].type, "application/json");
	strcpy(mime[8].type, "image/vnd.microsoft.icon");

	if (1 != getppid())
		demon();

	FILE *fp = freopen("/var/log/stderr.log", "w", stderr);
	if (fp == NULL) { 
			fprintf(stderr, "Cannot open file \n"); 
			exit(0); 
		}
	FILE *mime_stream = NULL;

	// Setter opp socket-strukturen
	sd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

	// For at operativsystemet ikke skal holde porten reservert etter tjenerens død
	setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &(int){1}, sizeof(int));

	// Initierer lokal adresse
	lok_adr.sin_family = AF_INET;
	lok_adr.sin_port = htons((u_short)LOKAL_PORT);
	lok_adr.sin_addr.s_addr = htonl(INADDR_ANY);

	//mount("none", "/proc", "proc", 0, NULL);

	// Kobler sammen socket og lokal adresse
	if (0 == bind(sd, (struct sockaddr *)&lok_adr, sizeof(lok_adr)))
	{
		fprintf(stderr, "Prosess %d er knyttet til port %d.\n", getpid(), LOKAL_PORT);
		fflush(stderr);
	}
	else
		exit(1);

	if (getuid() == 0)
	{
		/* process is running as root, drop privileges */
		if (setgid(1000) != 0)
			fprintf(stderr, "setgid: Unable to drop group privileges: %s", strerror(errno));
		if (setuid(1000) != 0)
			fprintf(stderr, "setuid: Unable to drop user privileges: %s", strerror(errno));
	}

	chdir("/var/www");
	chroot("/var/www/");

	// Venter på forespørsel om forbindelse
	listen(sd, BAK_LOGG);

	while (1)
	{

		mimeType = NULL;

		// Aksepterer mottatt forespørsel
		ny_sd = accept(sd, NULL, NULL);
		/*
		dup2(ny_sd, 0);
		fprintf(stdin, "%s", "string");
		*/
		recv(ny_sd, buffer, BUFFER_SIZE, 0);

		// fprintf(stderr, "Buffer data: %s\n #######################\n\n", buffer); DEBUG

		strtok(buffer, ". ");

		reqMessage = malloc(1050);

		reqMessage = strtok(NULL, ". ");
		if (reqMessage[0] == '/')
			reqMessage++;

		extension = (char *)strtok(NULL, ". ");

		fprintf(stderr, "%s - %s\n", extension, reqMessage);
		validFileType = 0;

		tmp = malloc(500);
		fprintf(stderr, "loggpunkt\n");

		if( strcmp((char*)extension,"asis") != 0 ){
			mime_stream = fopen("/etc/mime.types", "r");
			if (mime_stream == NULL) { 
				fprintf(stderr, "Cannot open file \n"); 
				exit(0); 
			} 
			fprintf(stderr, "loggpunkt2\n");
			while (fgets(buffer2, BUFFER_SIZE, mime_stream) != NULL)
			{
				for (char *str2 = buffer2;; str2 = NULL)
				{
					token = strtok_r(str2, "\t ", &savePtr2);
					if (token == NULL)
						break;
					for (int i = 0; i <= strlen(token); i++)
					{
						if (token[i] == '\n') //strlen(token) != 0
							token[strlen(token) - 1] = '\0';
					}
					//printf("-->%s<--\n", token);
					if (strstr(token, "/") != NULL)
					{
						strcpy(tmp, (char *)token);
					}
					else if (strcmp((char *)token, (char *)extension) == 0)
					{
						wait(NULL);
						mimeType = malloc(strlen(tmp)+100);
						strcpy(mimeType, tmp);
						break;
					}
				}
				if (mimeType != NULL)
					break;
			}
			fclose(mime_stream);
			//fp = freopen("/var/log/stderr.log", "a", stderr);
			fprintf(stderr, "asis-loggpunkt\n");
		}

		// Mellomlagrer for å slippe stack helvete
		free(tmp);
		tmp = malloc(500);
		strcpy(tmp, (char *)extension);

		// Prints for debugging
		fprintf(stderr, "%s\n", extension);
		fprintf(stderr, "%s\n", reqMessage);

		// Setter mimeType-variabelen til en tilfeldig streng
		if (mimeType == NULL)
		{
			mimeType = malloc((strlen("empty") + 1));
			strcpy(mimeType, "empty");
		}
		fprintf(stderr, "%s\n", mimeType); // debug print

		if( strcmp(tmp,"asis") == 0 ){
			reqMessage = strcat(reqMessage, ".");
			reqMessage = strcat(reqMessage, (char*)tmp);
			finalResponse = (char*)malloc(strlen(reqMessage));
			strcpy(finalResponse, reqMessage);
			reqMessage = NULL;
			validFileType = 1;
			fprintf(stderr, "%s\n\n", finalResponse);
		}
		else{
			// Sjekker om mime-typen finnes i structen som ble opprettet lenger opp i koden
			for (int i = 0; i <= (sizeof(mime) / sizeof(mime[0])); i++)
			{
				if (mimeType != NULL && strcmp(mimeType, mime[i].type) == 0)
				{
					//send(ny_sd,mime[i].type,strlen(mime[i].type),0);
					reqMessage = strcat(reqMessage, ".");
					reqMessage = strcat(reqMessage, (char *)tmp);
					finalResponse = malloc(strlen(reqMessage)+100);
					strcpy(finalResponse, reqMessage);
					reqMessage = NULL;
					validFileType = 1;
					fprintf(stderr, "%s\n\n", finalResponse);
				}
			}
		}

		// Låser opp allokert minne på heap-en
		fflush(stderr);
		//wait(NULL);
		//free(mimeType);

		if (validFileType == 0)
		{
			headerResponse(ny_sd, 1, 0, mimeType);
			if (0 == fork())
			{
				fflush(stdout);
				shutdown(ny_sd, SHUT_RDWR);
				exit(0);
			}
			else
			{
				free(reqMessage);
				free(tmp);
				free(finalResponse);
				free(mimeType);
				close(ny_sd);
			}
		}
		else 
		{
			//headerResponse(ny_sd, 0);

			if (0 == fork())
			{
				dup2(ny_sd, 1); // redirigerer socket til standard utgang
				//chroot("/var/www/");

				if (access(finalResponse, F_OK) != 0) {
					headerResponse(ny_sd, 2, 0, mimeType);
				}
				else{
					FILE *fptr = fopen(finalResponse, "rb"); // Åpner den forespurte filen
					if (fp == NULL) { 
						fprintf(stderr, "Cannot open file \n"); 
						exit(0); 
					} 
					fseek(fptr, 0, SEEK_END);
					int file_len = ftell(fptr);
					fseek(fptr, 0, SEEK_SET);

					headerResponse(ny_sd, 0, file_len, mimeType);

					int read_size;
					//int flag = 1;

					//setsockopt(ny_sd, IPPROTO_TCP, TCP_NODELAY, (char *) &flag, sizeof(int));
					while(0 < (read_size = fread(buffer, sizeof(char), file_len, fptr))){ 	// Leser fra filen
						send(ny_sd, buffer, read_size, 0);
						//fwrite(buffer, sizeof(char), read_size, ny_sd);
					}
					fflush(fptr);
					fclose(fptr);
				}
				

				// Sørger for å stenge socket for skriving og lesing
				// NB! Frigjør ingen plass i fildeskriptortabellen
				shutdown(ny_sd, SHUT_RDWR);
				exit(0);
			}
			else
			{
				free(reqMessage);
				free(tmp);
				free(finalResponse);
				free(mimeType);
				close(ny_sd);
			}
		}
	}
	return 0;
}

void headerResponse(int handler, int status, int cont_len, char* mime)
{

	char *header;
	header = (char *)malloc(1000);
	memset(header, 0, 1000);

	if (status == 0)
	{
		sprintf(header, "HTTP/1.1 200 OK\n\
						Content-Length: %d\n\
						Access-Control-Allow-Origin: *\n\
						Connection: keep-alive\n\
						Content-Range: none\n\
						Content-Type: %s;charset=UTF-8", cont_len, mime);
	}
	else if (status == 1)
	{
		strcpy(header, "HTTP/1.1 415 Unspported Media Type");
	}
	else
	{
		strcpy(header, "HTTP/1.1 404 Not Found");
	}
	if (strstr(header, "OK") == NULL)
	{
		fprintf(stderr, "%s\n", header);
		fflush(stderr);
	};
	strcat(header, "\r\n\r\n");
	write(handler, header, strlen(header));
	//send(handler, header, strlen(header), 0);
	free(header);
	//sleep(1);
}

void demon()
{

	/*
	Kode hentet fra: https://github.com/pasce/daemon-skeleton-linux-c
	*/

	pid_t pid;

	/* Fork off the parent process */
	pid = fork();

	/* An error occurred */
	if (pid < 0)
		exit(EXIT_FAILURE);

	/* Success: Let the parent terminate */
	if (pid > 0)
		exit(EXIT_SUCCESS);

	/* On success: The child process becomes session leader */
	if (setsid() < 0)
		exit(EXIT_FAILURE);

	/* Catch, ignore and handle signals */
	signal(SIGCHLD, SIG_IGN);
	signal(SIGHUP, SIG_IGN);

	/* Fork off for the second time*/
	pid = fork();

	/* An error occurred */
	if (pid < 0)
		exit(EXIT_FAILURE);

	/* Success: Let the parent terminate */
	if (pid > 0)
		exit(EXIT_SUCCESS);

	/* Set new file permissions */
	umask(0);

	/* Change the working directory to the root directory */
	/* or another appropriated directory */
	chdir("/home/nicwaa/Documents/da-nan/www");

	/* Close all open file descriptors */
	int x;
	for (x = sysconf(_SC_OPEN_MAX); x >= 0; x--)
	{
		close(x);
	}
}
