
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
#include <stdlib.h>

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
    const char *zookd_prog = "./zookd-exstack";
    int vulnerable_mode = 0;

    if (geteuid() != 0) {
        fprintf(stderr, "Must run zookld as root (sudo ./zookld)\n");
        return 1;
    }

    if (argc == 2) {
        if (strcmp(argv[1], "--vulnerable") == 0) {
            zookd_prog = "./zookd-vulnerable-exstack";
            vulnerable_mode = 1;
        } else if (strcmp(argv[1], "--fixed") != 0) {
            fprintf(stderr, "Usage: sudo ./zookld [--fixed|--vulnerable]\n");
            return 1;
        }
    } else if (argc > 2) {
        fprintf(stderr, "Usage: sudo ./zookld [--fixed|--vulnerable]\n");
        return 1;
    }

    
    if (chdir("/home/eitanbellaiche/Desktop/Shenkar/cyberSecurity/lab") != 0) {
        perror("chdir lab dir");
        return 1;
    }

    char *zookd_argv[] = {
        (char *) zookd_prog,
        "8080",
        NULL
    };

    char *tls_proxy_argv[] = {
        "./venv/bin/python",
        "tls_proxy.py",
        "8443",
        "127.0.0.1",
        "8080",
        "tls/server.crt",
        "tls/server.key",
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

    if (vulnerable_mode) {
        unsetenv("ZOOBAR_REQUIRE_TLS");
        unsetenv("ZOOBAR_TLS_PORT");
        setenv("ZOOBAR_DISABLE_CSRF", "1", 1);
    } else {
        setenv("ZOOBAR_REQUIRE_TLS", "1", 1);
        setenv("ZOOBAR_TLS_PORT", "8443", 1);
        unsetenv("ZOOBAR_DISABLE_CSRF");
    }

    pid_t zpid   = start_service("zookduser", zookd_argv);
    pid_t apid   = start_service("authuser",  auth_argv);
    pid_t bpid   = start_service("bankuser",  bank_argv);
    pid_t tpid   = -1;
    if (!vulnerable_mode) {
        tpid = start_service("zookduser", tls_proxy_argv);
    }

    printf("zookld: all services started.\n");
    printf("  %s pid = %d (user zookduser)\n", zookd_prog, zpid);
    printf("  auth-server   pid = %d (user authuser)\n",  apid);
    printf("  bank-server   pid = %d (user bankuser)\n",  bpid);
    if (!vulnerable_mode) {
        printf("  tls-proxy     pid = %d (user zookduser)\n", tpid);
        printf("  browse over HTTPS on https://localhost:8443/zoobar/index.cgi/\n");
    }

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
