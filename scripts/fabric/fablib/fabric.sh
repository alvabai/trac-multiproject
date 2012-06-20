# This script will provide auto completion for Fabric tasks in Bash shell
# Place this in /etc/bash_completion.d/ and start new shell
#
# The file is based on public gist: git://gist.github.com/1091866.git

_fab_commands=$(${fabbinpath} --fabfile=${fabfilepath} --shortlist)
_fab()
{
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    COMPREPLY=( $(compgen -W "${_fab_commands}" -- ${cur}) )
    case "${COMPREPLY}" in
        # commands i frequently add options to, add colon instead of space
        aws_name|aws_host)
            COMPREPLY="$COMPREPLY:"
            ;;
        *)
            COMPREPLY="$COMPREPLY "
            ;;
    esac

    return 0
}
complete -o nospace -F _fab fab
