include("PEM.jl")
include("alkaline.jl")


print("hello world\n")

# Alkaline model
# takes as input a vector of electricity input rates
# returns a vector of hydrogen output rates

"Calculates hydrogen (kg) outputs from alkaline electrolysis given electricity inputs \n
Takes: \n
    input: a vector of electricity input rates (kW) \n
    efficiency: the efficiency of the electrolyzer (0.5 by default) \n
    period: the time period over which the input is applied (s) (1.0 by default) \n
Outputs a vector of hydrogen output rates (kg/s) "
function alkaline(input::Vector{Float64}, efficiency::Float64=0.5, period::Float64=1.0)
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency
    end
    return output
end

# PEM model
# takes as input a vector of electricity input rates
# returns a vector of hydrogen output rates
"Calculates hydrogen outputs from PEM electrolysis given electricity inputs

"
function pem(input::Vector{Float64}, efficiency::Float64=0.6)
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency
    end
    return output
end

input = [1.0, 2.0, 3.0]
print(typeof(input))

print(alkaline(input))