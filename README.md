# What is it?
`essh` finds all ec2 instances in your AWS account with a `Name` tag value that matches a pattern and generates a simple menu.

# Example
```sh
$ essh host
##################################################
Pick from the following hosts (Ctrl C to escape):
##################################################
0> host00 | 10.0.0.10
1> host01 | 10.0.0.11
2> host02 | 10.0.0.12
```

You can also specify a user with the `--user` flag as well as only run one ssh command on a specific host:
Example:
```sh
$ essh --user mschurenko host00 uptime
 18:41:55 up 23:27,  0 users,  load average: 31.39, 30.37, 26.96
```

Run `essh --help` for the options.

# Prerequisites
- `ssh` must be in your path
- Your IAM access credentials need to come from some place (aws profile, env vars, etc).

# Installation
```sh
pip install git+https://github.com/mschurenko/essh.git
```
