
//   zookd-exstack 8080       כ-user zookduser
//   venv/bin/python auth…    כ-user authuser
//   venv/bin/python bank…    כ-user bankuser

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pwd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>

pid_t start_service(const char *username, char *const argv[])
{
    struct passwd *pw = getpwnam(username);
    if (!pw) {
        fprintf(stderr, "getpwnam(%s) failed\n", username);
        exit(1);
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(1);
    }

    if (pid == 0) {

        if (setgid(pw->pw_gid) != 0) {
            perror("setgid");
            exit(1);
        }
        if (setuid(pw->pw_uid) != 0) {
            perror("setuid");
            exit(1);
        }

       
        execv(argv[0], argv);

        perror("execv");
        fprintf(stderr, "execv failed for %s\n", argv[0]);
        exit(1);
    }

    printf("Started service '%s' as user %s with pid %d\n",
           argv[0], username, pid);
    return pid;
}

int main(int argc, char **argv)
{
    if (geteuid() != 0) {
        fprintf(stderr, "Must run zookld as root (sudo ./zookld)\n");
        return 1;
    }

    
    if (chdir("/home/eitanbellaiche/Desktop/Shenkar/cyberSecurity/lab") != 0) {
        perror("chdir lab dir");
        return 1;
    }

    char *zookd_argv[] = {
        "./zookd-exstack",
        "8080",
        NULL
    };

    char *auth_argv[] = {
        "./venv/bin/python",
        "zoobar/auth-server.py",
        "dummy",
        "/authsvc/sock",
        NULL
    };

    char *bank_argv[] = {
        "./venv/bin/python",
        "zoobar/bank-server.py",
        "dummy",
        "/banksvc/sock",
        NULL
    };

    pid_t zpid   = start_service("zookduser", zookd_argv);
    pid_t apid   = start_service("authuser",  auth_argv);
    pid_t bpid   = start_service("bankuser",  bank_argv);

    printf("zookld: all services started.\n");
    printf("  zookd-exstack pid = %d (user zookduser)\n", zpid);
    printf("  auth-server   pid = %d (user authuser)\n",  apid);
    printf("  bank-server   pid = %d (user bankuser)\n",  bpid);

    int status;
    pid_t dead;
    while ((dead = wait(&status)) > 0) {
        if (WIFEXITED(status)) {
            printf("Child %d exited with code %d\n",
                   dead, WEXITSTATUS(status));
        } else if (WIFSIGNALED(status)) {
            printf("Child %d killed by signal %d\n",
                   dead, WTERMSIG(status));
        }
    }

    return 0;
}
