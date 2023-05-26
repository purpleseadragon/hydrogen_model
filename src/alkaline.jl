# File for functions and variables related to alkaline model


"calculates hydrogen output rates from alkaline electrolysis given electricity inputs"
function alkaline(input::Vector{Float64}, efficiency::Float64=1, period::Float64=1.0)
    # working in kWh, kg and hours
    base = 55 # kWh/kg
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * efficiency * base
    end
    return output
end


function interpolate(x::Float64, x1::Float64, x2::Float64, y1::Float64, y2::Float64)
    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
end


function alk_output_v2(output_ratio::Vector{Float64}, power_range::Vector{Float64}, input::Vector{Float64})
    # working in kWh, kg and hours, want to return the rate of hydrogen output at each time step
    output = zeros(Float64, length(input))
    for i in 1:length(input)
        output[i] = input[i] * interpolate(input[i], power_range[1], power_range[2], output_ratio[1], output_ratio[2]) # multiplies input in KW by efficiency in kg/kWh to get kg / h ratio
    end
    return output
end



alk_parameters = Dict(
    "output_ratio" => [42.1, 48.8], # corresponding to capacity (stack) -> need to add additional ~10-20% for balance of plant
    "power_range" => [0.15*48.8*1750,48.8*1750], # kW 
    "min_load" => 0.15, # minimum load as a fraction of capacity
    "max_output" => 1750, # kg / hour
)

inputs = [5.0,6.0,7.0,9.0,11.0] # as Float64

interpolate(40000.0, 0.15*48.8*1750, 48.8*1750, 42.1, 48.8)

alk_output_v2(alk_parameters["output_ratio"], alk_parameters["power_range"], inputs)