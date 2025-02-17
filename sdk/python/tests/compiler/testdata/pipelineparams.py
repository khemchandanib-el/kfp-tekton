# Copyright 2020 kubeflow.org
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kfp import dsl
from kubernetes.client.models import V1EnvVar


@dsl.pipeline(name='pipeline-params', description='A pipeline with multiple pipeline params.')
def pipelineparams_pipeline(tag: str = 'latest', sleep_ms: int = 10):

    echo = dsl.Sidecar(
        name='echo',
        image='hashicorp/http-echo:%s' % tag,
        args=['-text="hello world"'],
    )

    op1 = dsl.ContainerOp(
        name='download',
        image='busybox:%s' % tag,
        command=['sh', '-c'],
        arguments=['sleep %s; wget localhost:5678 -O /tmp/results.txt' % sleep_ms],
        sidecars=[echo],
        file_outputs={'downloaded_resultOutput': '/tmp/results.txt'})

    op2 = dsl.ContainerOp(
        name='echo',
        image='library/bash',
        command=['sh', '-c'],
        arguments=['echo $MSG %s' % op1.output])
    
    op2.container.add_env_variable(V1EnvVar(name='MSG', value='pipelineParams: '))


if __name__ == '__main__':
    from kfp_tekton.compiler import TektonCompiler
    TektonCompiler().compile(pipelineparams_pipeline, __file__.replace('.py', '.yaml'))
