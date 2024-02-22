#!/bin/bash
name="azure-open-ai-trans"
Stop(){
    pid=$(ps -ef | grep "${name}" | grep -v grep | grep -v kill | awk '{print $2}')
    if [ -n "${pid}" ]; then
        echo "kill ${pid}"
        kill ${pid}
        for ((i=0; i<10; ++i)) do
            sleep 1
            pid=$(ps -ef | grep "${name}" | grep -v grep | grep -v kill | awk '{print $2}')
            if [ -n "${pid}" ]; then
                echo -e ".\c"
            else
                echo 'Stop Success!'
                break;
            fi
        done

        pid=$(ps -ef | grep "${name}" | grep -v grep | grep -v kill | awk '{print $2}')
        if [ -n "${pid}" ]; then
          echo "kill -9 ${pid}"
          pkill -9 ${pid}
        fi
    else
        echo "进程已关闭"
    fi
}

Start(){
    echo "开始启动"
    nohup python src/app.py --name=${name} &>/dev/null &
    for ((i=0; i<10; ++i)) do
        sleep 1
        pid=$(ps -ef | grep "${name}" | grep -v grep | grep -v kill | awk '{print $2}')
        if [ -z "${pid}" ]; then
            echo -e ".\c"
        else
            echo 'Start Success!'
            break;
        fi
    done

    pid=$(ps -ef | grep "${name}" | grep -v grep | grep -v kill | awk '{print $2}')
    if [ -z "${pid}" ]; then
      echo '启动失败'
    fi
}

case $1 in
    "start" )
        Start
    ;;
    "stop" )
       Stop
    ;;
    "restart" )
       Stop
       Start
    ;;
    * )
        echo "unknown command"
        exit 1
    ;;
esac